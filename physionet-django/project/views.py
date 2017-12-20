from django.contrib import messages
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import os

from .forms import (ProjectCreationForm, metadata_forms, MultiFileFieldForm,
    FolderCreationForm, MoveItemsForm, RenameItemForm)
from .models import Project, DatabaseMetadata, SoftwareMetadata
from .utility import (get_file_info, get_directory_info, get_storage_info,
    write_uploaded_file, list_items, remove_items, move_items)
from physionet.settings import MEDIA_ROOT, project_file_individual_limit
from user.forms import ProfileForm

import pdb


def download_file(request, file_path):
    """
    Serve a file to download. file_path is the full file path of the file on the server
    """
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            response = HttpResponse(f.read())
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            return response
    else:
        return Http404()


@login_required
def project_home(request):
    "Home page listing projects a user is involved in"
    
    user = request.user
    projects = Project.objects.filter(collaborators__in=[user])

    # Projects that the user is responsible for reviewing
    review_projects = None
    return render(request, 'project/project_home.html', {'projects':projects,
        'review_projects':review_projects})


@login_required
def create_project(request):
    user = request.user
    form = ProjectCreationForm(initial={'owner':user})

    if request.method == 'POST':
        form = ProjectCreationForm(request.POST)
        if form.is_valid() and form.cleaned_data['owner'] == user:
            project = form.save()
            return redirect('project_overview', project_id=project.id)

    return render(request, 'project/create_project.html', {'form':form})


@login_required
def project_overview(request, project_id):
    "Overview page of a project"
    user = request.user

    # Only allow access if the user is a collaborator
    # Turn this into a decorator, with login decorator
    project = Project.objects.get(id=project_id)
    collaborators = project.collaborators.all()
    if user not in collaborators:
        raise Http404("Unable to access project")

    return render(request, 'project/project_overview.html', {'project':project})


@login_required
def project_metadata(request, project_id):
    project = Project.objects.get(id=project_id)

    form = metadata_forms[project.resource_type.description](instance=project)

    if request.method == 'POST':
        form = metadata_forms[project.resource_type.description](request.POST,
            instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your project metadata has been updated.')
        else:
            messages.error(request,
                'There was an error with the information entered, please verify and try again.')

    return render(request, 'project/project_metadata.html', {'project':project,
        'form':form, 'messages':messages.get_messages(request)})



def selected_valid_items(request, selected_items, present_items):
    """
    Helper function to ensure selected files/folders are present in the
    directory
    """
    selected_items = request.POST.getlist('checks')

    if set(selected_items).issubset(present_items):
        return True
    else:
        messages.error(request, 'There was an error with the selected items.')
        return False


@login_required
def project_files(request, project_id, sub_item=''):
    "View and manipulate files in a project"
    project = Project.objects.get(id=project_id)

    # Directory where files are kept for the project
    project_file_root = project.file_root()

    # Case of accessing a file or subdirectory
    if sub_item:
        item_path = os.path.join(project_file_root, sub_item)
        # Serve a file
        if os.path.isfile(item_path):
            return download_file(request, item_path)
        # Invalid url
        elif not os.path.isdir(item_path):
            return Http404()
    
    # The url is not pointing to a file to download.

    # The file directory being examined
    file_dir = os.path.join(project_file_root, sub_item)
    # The contents of the directory
    file_names , dir_names = list_items(file_dir)
    item_names = file_names+dir_names
    storage_info = get_storage_info(project.storage_allowance*1024**3,
        project.storage_used())
    # Forms
    upload_files_form = MultiFileFieldForm(project_file_individual_limit,
        storage_info.remaining, item_names)
    folder_creation_form = FolderCreationForm()
    move_items_form = MoveItemsForm(dir_names)
    rename_item_form = RenameItemForm()

    if request.method == 'POST':
        if 'upload_files' in request.POST:
            upload_files_form = MultiFileFieldForm(project_file_individual_limit,
                storage_info.remaining, item_names, request.POST, request.FILES)

            if upload_files_form.is_valid():
                files = upload_files_form.files.getlist('file_field')
                for file in files:
                    write_uploaded_file(file=file,
                        write_file_path=os.path.join(file_dir, file.name))
                messages.success(request, 'Your files have been uploaded.')

        elif 'create_folder' in request.POST:
            folder_creation_form = FolderCreationForm(taken_names=item_names, data=request.POST)

            if folder_creation_form.is_valid():
                os.mkdir(os.path.join(file_dir, folder_creation_form.cleaned_data['folder_name']))
                messages.success(request, 'Your folder has been created.')

        elif 'delete_items' in request.POST:
            selected_items = request.POST.getlist('checks')
            if selected_valid_items(request, selected_items, item_names):
                remove_items([os.path.join(file_dir, i) for i in selected_items])
                messages.success(request, 'Your items have been deleted.')
            
        elif 'move_items' in request.POST:
            selected_items = request.POST.getlist('checks')
            move_items_form = MoveItemsForm(existing_subfolders=dir_names,
                selected_items=selected_items, current_directory=file_dir,
                data=request.POST)
            
            if selected_valid_items(request, selected_items, item_names) and move_items_form.is_valid():
                move_items([os.path.join(file_dir, i) for i in selected_items],
                    os.path.join(file_dir, move_items_form.cleaned_data['target_folder']))
                messages.success(request, 'Your items have been moved.')

        elif 'rename_item' in request.POST:
            selected_items = request.POST.getlist('checks')
            
            if len(selected_items) != 1:
                messages.error(request, 'You may only select one item at a time to rename.')

            if selected_valid_items(request, selected_items, item_names):
                #rename_item([os.path.join(file_dir, i) for i in selected_items]):
                messages.success(request, 'Your items have been moved.')


        # Reload the directory contents
        file_names , dir_names = list_items(file_dir)

    display_files = [get_file_info(os.path.join(file_dir, f)) for f in file_names]
    display_dirs = [get_directory_info(os.path.join(file_dir, d)) for d in dir_names]

    return render(request, 'project/project_files.html', {'project':project,
        'display_files':display_files, 'display_dirs':display_dirs,
        'sub_item':sub_item, 'storage_info':storage_info,
        'upload_files_form':upload_files_form, 'folder_creation_form':folder_creation_form,
        'move_items_form':move_items_form, 'rename_item_form':rename_item_form})


@login_required
def project_collaborators(request, project_id):
    project = Project.objects.get(id=project_id)
    return render(request, 'project/project_collaborators.html', {'project':project})
