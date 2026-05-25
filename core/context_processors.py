from django.utils.safestring import mark_safe
from .models import Slide, Category


def slides_processor(request):
    items = Slide.objects.filter(is_active=True).order_by('pk')
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
    items = Category.objects.filter(
        is_active=True).exclude(image='').order_by('title')
    item_div_list = ""
    items_div = ""
    for i, j in enumerate(items):
        if not i % 2:
            items_div += """<div class=\"block1 hov-img-zoom pos-relative m-b-30\"><img src=\"/media/{}\" alt=\"IMG-BENNER\"><div class=\"block1-wrapbtn w-size2\"><a href=\"/category/{}\" class=\"flex-c-m size2 m-text2 bg3 hov1 trans-0-4\">{}</a></div></div>""".format(
                j.image, j.slug, j.title)
        else:
            items_div_ = """<div class=\"block1 hov-img-zoom pos-relative m-b-30\"><img src=\"/media/{}\" alt=\"IMG-BENNER\"><div class=\"block1-wrapbtn w-size2\"><a href=\"/category/{}\" class=\"flex-c-m size2 m-text2 bg3 hov1 trans-0-4\">{}</a></div></div>""".format(
                j.image, j.slug, j.title)
            item_div_list += """<div class=\"col-sm-10 col-md-8 col-lg-4 m-l-r-auto\">""" + \
                items_div + items_div_ + """</div>"""
            items_div = ""

    return {"categories_div_html": mark_safe(item_div_list)}
