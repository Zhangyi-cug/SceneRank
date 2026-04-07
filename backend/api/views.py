import csv
import json
from datetime import datetime

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import SurveyConfig, ComparisonResult
from .serializers import ComparisonResultSerializer

DEFAULT_CONFIG = {
    "title": "街道环境偏好研究",
    "description": "本调查仅用于学术研究，不会泄露您的个人隐私",
    "coverImage": "",
    "background": {
        "title": "背景调查",
        "questions": [
            {
                "id": "age", "label": "您的年龄段", "type": "select", "required": True,
                "options": [
                    {"value": "18-25", "label": "18-25岁"},
                    {"value": "26-35", "label": "26-35岁"},
                    {"value": "36-60", "label": "36-60岁"},
                    {"value": "60+",   "label": "60岁及以上"}
                ]
            },
            {
                "id": "gender", "label": "您的性别", "type": "radio", "required": True,
                "options": [
                    {"value": "male",   "label": "男"},
                    {"value": "female", "label": "女"}
                ]
            },
            {
                "id": "experience", "label": "您的自行车使用频率", "type": "select", "required": True,
                "options": [
                    {"value": "5+",  "label": "每周5次以上"},
                    {"value": "3-5", "label": "每周3-5次"},
                    {"value": "1-3", "label": "每周1-3次"},
                    {"value": "0",   "label": "几乎不骑"}
                ]
            },
            {
                "id": "work", "label": "您从事什么职业", "type": "select", "required": True,
                "options": [
                    {"value": "student",  "label": "学生"},
                    {"value": "employed", "label": "固定职业"},
                    {"value": "freelance","label": "自由职业"},
                    {"value": "other",    "label": "非在职人员"}
                ]
            }
        ]
    },
    "comparison": {
        "instruction": "请对两张图片在以下各维度分别做出选择",
        "totalCount": 30,
        "imageRange": {"min": 1001, "max": 2010},
        "dimensions": [
            {"id": "safety",     "label": "🛡️ 安全 (Safety)",     "question": "在这条街上走动感觉有多安全？"},
            {"id": "beauty",     "label": "🌸 美丽 (Beauty)",      "question": "这条街看起来有多美？"},
            {"id": "liveliness", "label": "⚡ 活力 (Liveliness)",  "question": "这条街看起来有多繁华、有活力？"},
            {"id": "wealth",     "label": "💰 富裕 (Wealth)",      "question": "这条街看起来有多富裕？"},
            {"id": "boring",     "label": "😐 无聊 (Boring)",      "question": "这条街看起来有多单调乏味？"},
            {"id": "depressing", "label": "😔 压抑 (Depressing)",  "question": "这条街看起来有多令人压抑？"}
        ]
    }
}


def _check_admin(request):
    token = request.headers.get('X-Admin-Token', '') or request.GET.get('token', '')
    return token == settings.ADMIN_TOKEN


def _get_config():
    obj = SurveyConfig.objects.first()
    if obj:
        return obj.data
    return DEFAULT_CONFIG


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def config_view(request):
    if request.method == 'GET':
        return JsonResponse(_get_config())

    if not _check_admin(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    data = json.loads(request.body)
    obj, _ = SurveyConfig.objects.get_or_create(pk=1)
    obj.data = data
    obj.save()
    return JsonResponse({'ok': True})


@csrf_exempt
@require_http_methods(['POST'])
def config_reset(request):
    if not _check_admin(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    SurveyConfig.objects.filter(pk=1).delete()
    return JsonResponse(DEFAULT_CONFIG)


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def results_list(request):
    if request.method == 'POST':
        body = json.loads(request.body)
        ts = body.get('timestamp', datetime.utcnow().isoformat())
        result = ComparisonResult.objects.create(
            image_a=body['image_a'],
            image_b=body['image_b'],
            selections=body['selections'],
            background=body['background'],
            timestamp=ts
        )
        return JsonResponse({'id': result.id}, status=201)

    if not _check_admin(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    qs = ComparisonResult.objects.all()
    data = ComparisonResultSerializer(qs, many=True).data
    return JsonResponse(list(data), safe=False)


@csrf_exempt
@require_http_methods(['DELETE'])
def results_clear(request):
    if not _check_admin(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    count, _ = ComparisonResult.objects.all().delete()
    return JsonResponse({'deleted': count})


@csrf_exempt
@require_http_methods(['DELETE'])
def result_delete(request, pk):
    if not _check_admin(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    try:
        ComparisonResult.objects.get(pk=pk).delete()
        return JsonResponse({'ok': True})
    except ComparisonResult.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)


@require_http_methods(['GET'])
def results_export(request):
    if not _check_admin(request):
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    qs = ComparisonResult.objects.all().order_by('created_at')
    if not qs.exists():
        return JsonResponse({'error': 'No data'}, status=404)

    # 动态列头：从第一条记录推断
    first = qs.first()
    dim_keys = list(first.selections.keys())
    bg_keys = list(first.background.keys())

    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="scenerank_{datetime.now().strftime("%Y%m%d")}.csv"'

    writer = csv.writer(response)
    writer.writerow(['id', 'image_a', 'image_b'] + [f'sel_{d}' for d in dim_keys] + bg_keys + ['timestamp'])

    for r in qs:
        writer.writerow([
            r.id, r.image_a, r.image_b,
            *[r.selections.get(d, '') for d in dim_keys],
            *[r.background.get(k, '') for k in bg_keys],
            r.timestamp
        ])

    return response


@csrf_exempt
@require_http_methods(['POST'])
def admin_login(request):
    body = json.loads(request.body)
    password = body.get('password', '')
    if password == settings.ADMIN_TOKEN:
        return JsonResponse({'token': settings.ADMIN_TOKEN})
    return JsonResponse({'error': 'Invalid password'}, status=401)
