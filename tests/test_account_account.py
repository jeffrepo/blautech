from odoo import Command
from odoo.tests import TransactionCase, new_test_user, tagged


@tagged('post_install', '-at_install')
class TestAuditorAccountDisplayName(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env['res.company'].create({'name': 'Audit Company'})
        cls.other_company = cls.env['res.company'].create({'name': 'Other Audit Company'})
        companies = cls.company | cls.other_company
        cls.account = cls.env['account.account'].with_context(allowed_company_ids=companies.ids).create({
            'name': 'CAJA CHICA ADMINISTRACION',
            'description': 'Caja para gastos menores',
            'account_type': 'asset_cash',
            'company_ids': [Command.set(companies.ids)],
            'code_mapping_ids': [
                Command.create({'company_id': cls.company.id, 'code': '110101'}),
                Command.create({'company_id': cls.other_company.id, 'code': '210101'}),
            ],
        })
        user_values = {
            'company_id': cls.company.id,
            'company_ids': [Command.set(companies.ids)],
            'lang': 'en_US',
        }
        cls.auditor = new_test_user(
            cls.env, login='blautech_auditor',
            groups='base.group_user,blautech.auditoria_externa', **user_values,
        )
        cls.internal_user = new_test_user(
            cls.env, login='blautech_internal', groups='base.group_user', **user_values,
        )
        cls.account_reader = new_test_user(
            cls.env, login='blautech_account_reader',
            groups='base.group_user,account.group_account_readonly', **user_values,
        )

    def test_auditor_sees_code_without_extra_permissions(self):
        account = self.account.with_user(self.auditor)
        self.assertFalse(self.auditor.has_group('account.group_account_readonly'))
        self.assertEqual(account.display_name, '110101 CAJA CHICA ADMINISTRACION')
        self.assertTrue(account.has_access('read'))
        for operation in ('write', 'create', 'unlink'):
            self.assertFalse(account.has_access(operation))

    def test_display_name_cache_is_user_specific(self):
        for user, expected in (
            (self.internal_user, 'CAJA CHICA ADMINISTRACION'),
            (self.auditor, '110101 CAJA CHICA ADMINISTRACION'),
            (self.account_reader, '110101 CAJA CHICA ADMINISTRACION'),
            (self.internal_user, 'CAJA CHICA ADMINISTRACION'),
        ):
            with self.subTest(user=user.login):
                self.assertEqual(self.account.with_user(user).display_name, expected)

    def test_formatted_name_keeps_suggestion_and_description(self):
        account = self.account.with_context(
            formatted_display_name=True,
            preferred_account_ids=self.account.ids,
            lang='en_US',
        )
        expected = '110101 CAJA CHICA ADMINISTRACION `Suggested`\n--Caja para gastos menores--'
        self.assertEqual(account.with_user(self.auditor).display_name, expected)
        self.assertEqual(account.with_user(self.account_reader).display_name, expected)

    def test_native_accounting_group_does_not_duplicate_code(self):
        self.account_reader.write({
            'group_ids': [Command.link(self.env.ref('blautech.auditoria_externa').id)],
        })
        account = self.account.with_user(self.account_reader)
        self.assertEqual(account.display_name, '110101 CAJA CHICA ADMINISTRACION')
        self.assertEqual(
            account.with_context(formatted_display_name=True).display_name,
            '110101 CAJA CHICA ADMINISTRACION\n--Caja para gastos menores--',
        )

    def test_code_follows_active_company(self):
        account = self.account.with_user(self.auditor)
        self.assertEqual(account.with_company(self.company).display_name, '110101 CAJA CHICA ADMINISTRACION')
        self.assertEqual(account.with_company(self.other_company).display_name, '210101 CAJA CHICA ADMINISTRACION')
        self.assertEqual(account.with_company(self.company).display_name, '110101 CAJA CHICA ADMINISTRACION')

    def test_account_without_code_keeps_name(self):
        account = self.env['account.account'].with_user(self.auditor).with_context(
            allowed_company_ids=self.company.ids,
        ).new({
            'name': 'Cuenta sin código',
            'code': False,
        })
        self.assertEqual(account.display_name, 'Cuenta sin código')
        self.assertEqual(
            account.with_context(formatted_display_name=True).display_name,
            'Cuenta sin código',
        )
