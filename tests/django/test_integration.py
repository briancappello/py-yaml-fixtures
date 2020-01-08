import pytest

from contextlib import redirect_stdout

from django.core.management import call_command

from django_test_app.models import User, Article, Category, Tag


@pytest.mark.django_db
class TestUser:
    def test_it(self, django_db_blocker):
        with django_db_blocker.unblock():
            with redirect_stdout(None):
                call_command("import_fixtures", "django_test_app")

        users = set(User.objects.values_list("username", flat=True))
        assert users == {"grace", "judy"}

        categories = set(Category.objects.values_list("name", flat=True))
        assert categories == {"Food", "Vacation"}

        tags = set(Tag.objects.values_list("name", flat=True))
        assert tags == {"Italian",
                        "Mexican",
                        "Chinese",
                        "South East Asia",
                        "United States of America",
                        "Canada"}

        assert Article.objects.count() == 3

        article_one = Article.objects.get(title="Pasta in Canada")
        assert article_one.author.username == "grace"
        assert article_one.category.name == "Food"
        assert set(article_one.tags.values_list("name", flat=True)) == {"Italian", "Canada"}

        article_two = Article.objects.get(title="Chinese in SEA")
        assert article_two.author.username == "grace"
        assert article_two.category.name == "Food"
        assert set(article_two.tags.values_list("name", flat=True)) == {"Chinese",
                                                                        "South East Asia"}

        article_three = Article.objects.get(title="Vacation in America")
        assert article_three.author.username == "judy"
        assert article_three.category.name == "Vacation"
        assert set(article_three.tags.values_list("name", flat=True)) == {
            "United States of America", "Mexican"}
