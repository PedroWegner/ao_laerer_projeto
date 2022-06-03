from django.contrib import messages


def send_message_success(request, message: str) -> None:
    messages.add_message(
        request,
        messages.SUCCESS,
        message
    )


def send_message_error(request, message: str) -> None:
    messages.add_message(
        request,
        messages.ERROR,
        message
    )


def send_message_info(request, message: str) -> None:
    messages.add_message(
        request,
        messages.INFO,
        message
    )
