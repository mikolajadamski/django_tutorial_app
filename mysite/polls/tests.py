from django.test import TestCase

import datetime
from django.utils import timezone
from .models import Question
from django.urls import reverse
# Create your tests here.

class QuestionModelTests(TestCase):
    
    def test_was_published_recently_with_future_question(self):
        """
        was_published_recently() returns False for questions whose pub_date is in the future.
        """
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        """
        was_published_recently() returns False for questions whose pub_date is older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        """
        was_published_recently() returns True for questions whose pub_date is not older than 1 day.
        """
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

def create_question(question_text, days):
    time = timezone.now() + datetime.timedelta(days=days)
    return Question.objects.create(question_text=question_text, pub_date=time)


class QuestionIndexViewTests(TestCase):
    def test_no_questions(self):
        """
        If no questions, message is displayed.
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'],[])

    def test_past_question(self):
        """
        If question with pub_date in the past, question is displayed.
        """
        create_question(question_text="Past question", days=-2)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'],['<Question: Past question>'])

    def test_future_question(self):
        """
        If question with pub_date in the future, question is not displayed.
        """
        create_question(question_text="Future question", days=2)
        response = self.client.get(reverse('polls:index'))
        self.assertContains(response, "No polls are available.")
        self.assertQuerysetEqual(response.context['latest_question_list'], [])

    def test_future_question_and_past_question(self):
        """
        If both past question and future question exist, show only past question.
        """
        create_question(question_text="Past question", days=-2)
        create_question(question_text="Future question", days=2)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], ['<Question: Past question>'])

    def test_two_past_questions(self):
        """
        If multiple past questions, show them, more recent first.
        """
        create_question(question_text="Past question 1", days=-3)
        create_question(question_text="Past question 2", days=-2)
        response = self.client.get(reverse('polls:index'))
        self.assertQuerysetEqual(response.context['latest_question_list'], 
        ['<Question: Past question 2>', '<Question: Past question 1>'])

    
class QuestionDetailViewTests(TestCase):
    def test_future_question(self):
        """
        Detail view of question from future returns 404 error.
        """
        future_question = create_question(question_text='Future question', days=5)
        url = reverse('polls:detail', args=(future_question.id,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_past_question(self):
        """
        Detail view of question from the past displays text of the question
        """
        past_question = create_question(question_text="Past question",days=-2)
        url = reverse('polls:detail', args=(past_question.id,))
        response = self.client.get(url)
        self.assertContains(response, past_question.question_text)

#TODO: Add tests for ResultsView.