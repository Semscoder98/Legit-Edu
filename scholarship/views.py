from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Scholarship, ScholarshipComment
from .serializers import ScholarshipSerializer


def scholarship_list(request):
    scholarships = Scholarship.objects.filter(is_active=True)
    level = request.GET.get('level')
    if level:
        scholarships = scholarships.filter(level=level)
    paginator = Paginator(scholarships, 9)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'scholarship/list.html', {'page_obj': page_obj, 'active_level': level})


def scholarship_detail(request, slug):
    scholarship = get_object_or_404(Scholarship, slug=slug, is_active=True)
    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        guest_name = request.POST.get('guest_name', '').strip() or 'Anonymous'
        parent_id = request.POST.get('parent_id')
        parent = None
        if parent_id:
            parent = ScholarshipComment.objects.filter(id=parent_id, scholarship=scholarship).first()
        if body:
            ScholarshipComment.objects.create(
                scholarship=scholarship,
                guest_name=guest_name,
                parent=parent,
                body=body,
            )
        return redirect('scholarship_detail', slug=scholarship.slug)
    comments = scholarship.comments.filter(is_approved=True, parent__isnull=True).order_by('created_at')
    comment_count = scholarship.comments.filter(is_approved=True).count()
    return render(request, 'scholarship/detail.html', {'scholarship': scholarship, 'comments': comments, 'comment_count': comment_count})


class ScholarshipViewSet(viewsets.ModelViewSet):
    queryset = Scholarship.objects.filter(is_active=True)
    serializer_class = ScholarshipSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
