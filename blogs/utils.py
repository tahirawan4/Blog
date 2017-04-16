from blogs.models import Category


def get_all_visible_categories():
    return Category.objects.filter(hidden=False)
