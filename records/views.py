from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from records.serializers import RecordSerializer

from krwordrank.word import summarize_with_keywords
from .models import Record

import os
from django.http import FileResponse
from wordcloud import WordCloud
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from django.conf import settings

@api_view(['GET', 'POST'])
def record(request):
    match request.method:
        case 'GET':
            records = Record.objects.all()
            serializer = RecordSerializer(records, many=True)
            return Response(serializer.data)
        case 'POST':
            record_serializer = RecordSerializer(data=request.data)
            if not record_serializer.is_valid():
                return Response(record_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            record_serializer.save()
            return Response(record_serializer.data, status=status.HTTP_201_CREATED)


def generate_wordcloud(frequencies, stopwords):
    font_path = "C:/monic_Data/홍익대학교/멋사/Mindary/WordCloud/DungGeunMo.woff"

    wordcloud = WordCloud(
        width=800, height=400, 
        background_color='white', 
        stopwords=stopwords,
        font_path=font_path
    ).generate_from_frequencies(frequencies)
    return wordcloud.to_image()

@api_view(['GET'])
def records_wordcloud(request, category):
    # 데이터 담기
    records = Record.objects.filter(category=category)
    texts = [record.content for record in records]
    if not texts:
        return Response({"message": "No text content found in records"}, status=404)
    
    # 불용어
    stopwords = {
        '너무', '정말', '아주', '매우', '굉장히', '상당히', '무척', '엄청', '몹시', '너무나', '대단히', '정말로', '실로', '진짜', '참으로', 
        '물론', '다소', '약간', '조금', '많이', '그야말로', '대단히', '일부', '더욱', '특히',
        '을', '를', '에', '의', '이', '가', '은', '는', '도', '로', '와', '과', '제', '한', '그', '저', '이', '각', '것', '수', '듯', '바',
        '그리고', '그러고', '그러나', '그래서', '그러면', '그러나', '그렇지만',
        '것을', '것이', '있는', '싶다', '나니', '때문', '이런', '저런', '그런', '어떤', '모든', '아무', '통해', '다시', '마치',
        '어제', '내일', '모레', '지금', '그때', '언제', '항상', '자주', '가끔', '때때로', '이번', '다음',
        '이렇게', '것을', '같다.', '되었다.', '남았다.', '.', '같은', '있었', '했어.', 

        # '오늘', 
        } 
    keywords = summarize_with_keywords(
        texts, min_count=1, max_length=10, # NLP
        beta=0.85, max_iter=10, stopwords=stopwords, verbose=True )

    # 워드 클라우드 생성
    word_frequencies = {key: val for key, val in keywords.items()}
    wordcloud_image = generate_wordcloud(word_frequencies, stopwords)

    # 이미지 파일로 변환
    image_path = os.path.join(settings.MEDIA_ROOT, "wordcloud.png")
    wordcloud_image.save(image_path)

    if not os.path.exists(image_path):
        print("Image file was not saved.")
        return Response({"message": "Failed to save image file"}, status=500)

    return Response({"message": "png 생성 완료"}, status=200)