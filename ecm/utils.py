# -*- coding: utf-8 -*-
# Author: Christian Douglas <christian.douglas.alcantara@gmail.com>
import os
from functools import wraps
from .models import Attachment


def combine_chunks(total_parts, total_size, source_folder, dest):
    """ Combine a chunked file into a whole file again. Goes through each part
    , in order, and appends that part's bytes to another destination file.

    Chunks are stored in media/chunks
    Uploads are saved in media/uploads
    """

    if not os.path.exists(os.path.dirname(dest)):
        os.makedirs(os.path.dirname(dest))

    with open(dest, 'wb+') as destination:
        for i in range(total_parts):
            part = os.path.join(source_folder, str(i))
            with open(part, 'rb') as source:
                destination.write(source.read())


def save_upload(f, path):
    """ Save an upload. Django will automatically "chunk" incoming files
    (even when previously chunked by fine-uploader) to prevent large files
    from taking up your server's memory. If Django has chunked the file, then
    write the chunks, otherwise, save as you would normally save a file in
    Python.

    Uploads are stored in media/uploads
    """
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    with open(path, 'wb+') as destination:
        if hasattr(f, 'multiple_chunks') and f.multiple_chunks():
            for chunk in f.chunks():
                destination.write(chunk)
        else:
            destination.write(f.read())


def get_attachment_model_name(model_attachment):
    return model_attachment._meta.app_label.lower() + '.' + \
           model_attachment.__name__.lower()


def attachment_form_valid(f):
    @wraps(f)
    def wrapper(object_instance, form):
        f(object_instance, form)
        if object_instance.model.use_upload:
            files = object_instance.request.FILES.getlist('file')
            if files:
                instance = object_instance.object
                for file in files:
                    model_name = get_attachment_model_name(object_instance.model)
                    attachment = Attachment(
                        model_name=model_name,
                        object_id=instance.id,
                        file=file,
                        exibition_name=file.name,
                        create_user_id=object_instance.request.user.id
                    )
                    attachment.save()
        return f(object_instance, form)
    return wrapper


def attachments_multi_delete(model_attachment, pks=[],):
    model_name = get_attachment_model_name(model_attachment)
    if Attachment.objects.filter(model_name=model_name) \
            .filter(object_id__in=pks):
        Attachment.objects.filter(model_name=model_name) \
            .filter(object_id__in=pks).delete()
