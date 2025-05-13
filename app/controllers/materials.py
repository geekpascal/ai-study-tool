from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.material import Material
from app.forms.material import MaterialForm, MaterialProgressForm
from werkzeug.utils import secure_filename
from app.services.pdf_service import extract_pdf_info
import os
from datetime import datetime

materials_bp = Blueprint('materials', __name__, url_prefix='/materials')

@materials_bp.route('/')
@login_required
def index():
    materials = Material.query.filter_by(user_id=current_user.id).all()
    return render_template('materials/index.html', materials=materials)

@materials_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = MaterialForm()
    if form.validate_on_submit():
        # Handle file upload
        file = form.file.data
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            file_type = filename.split('.')[-1].lower()
            
            # Extract PDF info if applicable
            total_pages = 0
            if file_type == 'pdf':
                total_pages = extract_pdf_info(file_path)
        else:
            file_path = None
            file_type = None
            total_pages = form.total_pages.data or 0
        
        # Create material
        material = Material(
            title=form.title.data,
            description=form.description.data,
            file_path=file_path,
            file_type=file_type,
            total_pages=total_pages,
            deadline=form.deadline.data,
            user_id=current_user.id
        )
        
        db.session.add(material)
        db.session.commit()
        flash('Material added successfully!', 'success')
        return redirect(url_for('materials.index'))
    
    return render_template('materials/create.html', form=form)

@materials_bp.route('/<int:id>')
@login_required
def show(id):
    material = Material.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    return render_template('materials/show.html', material=material)

@materials_bp.route('/<int:id>/progress', methods=['GET', 'POST'])
@login_required
def update_progress(id):
    material = Material.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = MaterialProgressForm(obj=material)
    
    if form.validate_on_submit():
        form.populate_obj(material)
        db.session.commit()
        flash('Progress updated!', 'success')
        return redirect(url_for('materials.show', id=material.id))
    
    return render_template('materials/progress.html', form=form, material=material)

@materials_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    material = Material.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(material)
    db.session.commit()
    flash('Material deleted successfully!', 'success')
    return redirect(url_for('materials.index')) 