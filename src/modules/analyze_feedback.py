from src.modules.base               import BaseModule
from src.utils              import Utils
from src.animation_utils    import start_animation
import threading
from textblob import TextBlob
from googletrans    import Translator, LANGUAGES


class FeedbackAnalyzer(BaseModule):

    def translate_to_english(self, comments):
        done_event = threading.Event()
        loading_thread = start_animation(done_event, 'translating comments')
        translator = Translator()
        translated_comments = []

        for comment in comments:
            if comment is None:
                continue
            try:
                detected = translator.detect(comment)
                if LANGUAGES[detected.lang] != 'en':
                    translated_comment = translator.translate(comment, dest='en').text
                    translated_comments.append(translated_comment)
                else:
                    translated_comments.append(comment)
            except Exception as e:
                self.logs.error(f'\rtranslation error: {e}')
                translated_comments.append(comment)

        done_event.set()
        loading_thread.join()

        return translated_comments


    def run(self):
        login = input('login: ')
        
        try:
            done_event = threading.Event()
            loading_thread = start_animation(done_event, 'fetching data')
            teams = Utils.get_evaluations_for_user(self.api, Utils.get_user_id(self.api, login), side='as_corrected')
        except Exception as e:
            return f'error: {e}'
        finally:
            done_event.set()
            loading_thread.join()
        
        comments = self.translate_to_english(teams['comment'])
        negative_comments = []
        done_event = threading.Event()
        loading_thread = start_animation(done_event, 'analyzing comments')
        positive, neutral, negative = 0, 0, 0
        for comment in comments:
            blob = TextBlob(comment)
            if blob.sentiment.polarity > 0:
                positive += 1
            elif blob.sentiment.polarity == 0:
                neutral += 1
            else:
                negative += 1
                negative_comments.append(comment)
        done_event.set()
        loading_thread.join()
        formatted_negative_comments = '\n-\n'.join(negative_comments)
        return f'{len(negative_comments)} negative comments found:\n-\n{formatted_negative_comments}'
