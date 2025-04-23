from flask import Blueprint, render_template, request, redirect, url_for, flash
import os

report_bp = Blueprint('report', __name__, url_prefix='/report')

@report_bp.route('/', methods=['GET', 'POST'])
def report_issue():
    if request.method == 'POST':
        issue = request.form['issue']
        description = request.form['description']
        location = request.form['location']
        file = request.files.get('file')

        # Save file
        if file and file.filename != '':
            filepath = os.path.join('app/static/uploads', file.filename)
            file.save(filepath)

        # Flash message (replace with DB saving later)
        flash('Issue reported successfully!')
        return redirect(url_for('report.report_issue'))

    return render_template('report.html')
