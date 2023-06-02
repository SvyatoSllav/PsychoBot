from psycho_survey.models import Review

from telegram_bot.models import TelegramUser


class ReviewValidators:
    @classmethod
    def _review_exists(cls, user: TelegramUser):
        return Review.objects.filter(user=user).exists()


class ValidatorsMixin(ReviewValidators):
    pass


class MessageHandlers:
    pass
