from django.utils.safestring import mark_safe
from .models import Slide, Category


def slides_processor(request):
    try:
        items = Slide.objects.filter(is_active=True).order_by('pk')
    except Exception:
        return {"slides_html": mark_safe('')}
    out = []
    for s in items:
        img = s.image.url if hasattr(s.image, 'url') else s.image
        html = (
            f"<div class=\"item-slick1 item2-slick1\" style=\"background-image: url({img}); background-size:cover; background-position:center;\">"
            "<div class=\"wrap-content-slide1 sizefull flex-col-c-m p-l-15 p-r-15 p-t-150 p-b-170 hero\">"
            f"<div style=\"max-width:1100px;margin:0 auto;padding:24px;\">"
            f"<span class=\"caption1-slide1 m-text1 t-center\">{s.caption1}</span>"
            f"<h2 class=\"caption2-slide1 xl-text1 t-center\" style=\"font-family: 'Merriweather', serif;\">{s.caption2}</h2>"
            f"<div class=\"wrap-btn-slide1\"><a href=\"{s.link}\" class=\"btn-primary-uh\">Shop Now</a></div>"
            "</div></div></div>"
        )
        out.append(html)
    return {"slides_html": mark_safe(''.join(out))}


def categories_processor(request):
    categories = Category.objects.filter(
        is_active=True).exclude(image='').order_by('title')
    return {"categories": categories}
