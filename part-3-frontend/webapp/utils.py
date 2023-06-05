from werkzeug.datastructures import FileStorage


def _is_image(storage: FileStorage):
    return storage.content_type.split('/')[0] == "image"
