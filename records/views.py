from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from records.serializers import RecordSerializer

from krwordrank.word import summarize_with_keywords
from .models import Record

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


@api_view(['GET'])
def records_wordcloud(request, category):
    records = Record.objects.filter(category=category)
    texts = []
    for record in records: # 데이터 전처리
        texts.append(record.content) 
    stopwords = {'너무', '정말', '매우', '일부'} # 불용어
    keywords = summarize_with_keywords(texts, min_count=1, max_length=10, # NLP
        beta=0.85, max_iter=10, stopwords=stopwords, verbose=True)

    wordlist = []
    count = 0
    for key, val in keywords.items(): # 다음 라이브러리를 위한 후처리
        temp = {'name': key, 'value': int(val*100)}
        wordlist.append(temp)
        count += 1
        if count >= 30: # 출력 수 제한
            break

    return Response(wordlist)