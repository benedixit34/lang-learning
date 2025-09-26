from pathlib import Path

from django.core.files import File
from django.core.files.storage import FileSystemStorage
from django.shortcuts import get_object_or_404

from celery import shared_task

from .models import Lesson, Video
from .utils import cleanup_files, upload_image_to_cloudinary, upload_video_to_cloudinary

# /courses/${course_id}/lessons/${lesson_id}/videos


@shared_task
def upload_video_lesson(video_metadata, image_metadata):
    video_file_path = video_metadata.pop("file_path")
    image_file_path = image_metadata.pop("file_path")

    video_file_name = video_metadata.pop("file_name")
    image_file_name = image_metadata.pop("file_name")

    fs = FileSystemStorage()
    video_path_object = Path(video_file_path)
    image_path_object = Path(image_file_path)

    try:
        with image_path_object.open(mode="rb") as file:
            image = File(file, name=image_path_object.name)
            image_url = upload_image_to_cloudinary(image)

        with video_path_object.open(mode="rb") as file:
            video = File(file, name=video_path_object.name)
            video_url = upload_video_to_cloudinary(video)
        lesson_uuid = video_metadata.pop("lesson")
        lesson = get_object_or_404(Lesson, uuid=lesson_uuid)
        video = Video.objects.create(
            lesson=lesson, video=video_url, featured_image=image_url, **video_metadata
        )

    except Exception as e:
        fs.delete(video_file_name)
        fs.delete(image_file_name)

    finally:
        cleanup_files(fs, video_file_name, image_file_name)
