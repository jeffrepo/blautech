from unittest.mock import patch

from odoo import Command
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestPaymentEntryPosting(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.payment_currency = cls.setup_other_currency('EUR')
        cls.payment_journal = cls.company_data['default_journal_credit']
        cls.payment_journal.currency_id = cls.payment_currency
        cls.payment_method_line = cls.payment_journal.outbound_payment_method_line_ids.filtered(
            lambda line: line.payment_method_id.code == 'manual'
        )
        cls.payment_method_line.ensure_one()
        cls.outstanding_account = cls.env['account.account'].create({
            'name': 'Card payments pending',
            'code': 'BLAUPAY',
            'account_type': 'liability_current',
            'reconcile': False,
            'company_ids': [Command.set(cls.env.company.ids)],
        })
        cls.payment_method_line.payment_account_id = cls.outstanding_account

    def _make_bill(self):
        bill = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': self.partner_a.id,
            'journal_id': self.company_data['default_journal_purchase'].id,
            'currency_id': self.company_data['currency'].id,
            'invoice_date': '2024-01-01',
            'date': '2024-01-01',
            'invoice_payment_term_id': False,
            'invoice_line_ids': [Command.create({
                'name': 'Service',
                'quantity': 1,
                'price_unit': 100,
                'account_id': self.company_data['default_account_expense'].id,
                'tax_ids': [Command.clear()],
            })],
        })
        bill.action_post()
        return bill

    def _pay_bill(self, bill, amount=100, expected_before_confirmation='paid'):
        wizard = self.env['account.payment.register'].with_context(
            active_model='account.move', active_ids=bill.ids,
        ).create({
            'journal_id': self.payment_journal.id,
            'payment_method_line_id': self.payment_method_line.id,
            'payment_date': bill.date,
            'currency_id': self.payment_currency.id,
            'amount': bill.currency_id._convert(
                amount, self.payment_currency, bill.company_id, bill.date,
            ),
        })
        original_init = type(wizard)._init_payments
        snapshots = []

        def init_and_recompute(wizard, to_process, edit_mode=False):
            payments = original_init(wizard, to_process, edit_mode=edit_mode)
            # Exercise the problematic recomputation order before confirmation,
            # retaining the real create, post and reconciliation implementations.
            self.env.add_to_compute(payments._fields['state'], payments)
            payments._recompute_recordset(['state'])
            snapshots.extend((payment.state, payment.move_id.state) for payment in payments)
            return payments

        with patch.object(type(wizard), '_init_payments', init_and_recompute):
            payment = wizard._create_payments()
        payment.ensure_one()
        self.assertEqual(snapshots, [(expected_before_confirmation, 'draft')])
        self.assertEqual(payment.move_id.state, 'posted')
        return payment

    def test_non_reconcilable_account_posts_and_pays_bill(self):
        bill = self._make_bill()
        payment = self._pay_bill(bill)
        self.assertEqual(payment.state, 'paid')
        self.assertTrue(payment.is_reconciled)
        self.assertEqual(bill.amount_residual, 0)
        self.assertEqual(bill.payment_state, 'paid')

    def test_reconcilable_account_keeps_bill_in_payment(self):
        self.outstanding_account.reconcile = True
        bill = self._make_bill()
        payment = self._pay_bill(bill, expected_before_confirmation='in_process')
        self.assertEqual(payment.state, 'in_process')
        self.assertEqual(bill.amount_residual, 0)
        self.assertEqual(bill.payment_state, 'in_payment')

    def test_partial_payment_keeps_remaining_balance(self):
        bill = self._make_bill()
        self._pay_bill(bill, amount=40)
        self.assertEqual(bill.amount_residual, 60)
        self.assertEqual(bill.payment_state, 'partial')

    def test_confirming_again_keeps_same_entry_and_reconciliation(self):
        bill = self._make_bill()
        payment = self._pay_bill(bill)
        move = payment.move_id
        name = move.name
        lines = move.line_ids
        payment.action_post()
        self.assertEqual(payment.move_id, move)
        self.assertEqual(move.name, name)
        self.assertEqual(move.line_ids, lines)
        self.assertEqual(move.state, 'posted')
        self.assertEqual(bill.amount_residual, 0)
        self.assertEqual(bill.payment_state, 'paid')

    def test_payment_without_outstanding_account_keeps_native_flow(self):
        self.payment_method_line.payment_account_id = False
        bill = self._make_bill()
        payment = self.env['account.payment.register'].with_context(
            active_model='account.move', active_ids=bill.ids,
        ).create({
            'journal_id': self.payment_journal.id,
            'payment_method_line_id': self.payment_method_line.id,
            'payment_date': bill.date,
        })._create_payments()
        self.assertFalse(payment.move_id)
        self.assertEqual(payment.state, 'in_process')
        self.assertEqual(bill.amount_residual, 100)
        self.assertEqual(bill.payment_state, 'in_payment')
