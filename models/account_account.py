from odoo import api, models


class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.depends('code', 'name', 'description')
    @api.depends_context('company', 'uid', 'formatted_display_name')
    def _compute_display_name(self):
        super()._compute_display_name()
        if (
            not self.env.user.has_group('blautech.auditoria_externa')
            or self.env.user.has_group('account.group_account_readonly')
        ):
            return

        # Odoo 19 hides the code without the standard accounting group. Keep
        # the auditor's existing permissions and the native formatted suffixes.
        separator = '' if self.env.context.get('formatted_display_name') else ' '
        for account in self:
            if account.code:
                account.display_name = f'{account.code}{separator}{account.display_name}'
