from odoo import models


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        result = super().action_post()
        # A non-reconcilable outstanding account can make the payment "paid"
        # before its entry is posted. Core confirmation then skips that payment.
        moves_to_post = self.filtered(
            lambda payment: payment.state in ('in_process', 'paid')
            and payment.move_id.state == 'draft'
        ).move_id
        if moves_to_post:
            moves_to_post.action_post()
        return result
