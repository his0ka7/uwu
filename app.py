
from flask import\
    Flask,\
    render_template,\
    jsonify,\
    redirect,\
    url_for,\
    flash,\
    request,\
    send_file
import datetime

@app.route('/invoice_data', methods=['GET', 'POST'])
def invoice_form():
        invoice_details = InvoiceDetails.query.one_or_none()
        positions_form = PositionsForm(prefix='positions')
        invoice_form = InvoiceForm(prefix='invoice', obj=invoice_details)

        if request.method == 'POST':
            if positions_form.validate_on_submit():
                unit = positions_form.unit.data
                amount = positions_form.amount.data
                price = positions_form.price.data
                description = positions_form.description.data
                total = amount * price
                new_position = Positions(
                    unit=unit,
                    amount=amount,
                    price=price,
                    description=description,
                    total=total
                )
                new_position.insert()

                flash('Position succesfully added!', 'success')
            elif invoice_form.validate_on_submit():
                form_invoice_details = invoice_form.data
                form_invoice_details.pop('csrf_token', None)
                if invoice_details is None:
                    invoice_details = InvoiceDetails(**form_invoice_details)
                    invoice_details.insert()
                else:
                    invoice_details.update(**form_invoice_details)

                positions = Positions.query.all()
                total = 0
                for position in positions:
                    total += position.total
                created = datetime.date.today()
                payment_due = created + datetime.timedelta(days=14)

                return render_template('/invoice_details.html',
                                       title='Invoice Details',
                                       invoice_details=invoice_details,
                                       positions=positions,
                                       created=created,
                                       payment_due=payment_due,
                                       total=total
                                       )
            else:
                flash('Please check your form input!', 'error')

        positions = Positions.query.all()

        return render_template(
            '/invoice_form.html',
            title='Invoice Form',
            active_page='form',
            positions_form=positions_form,
            invoice_form=invoice_form,
            positions=positions
        )