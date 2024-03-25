from src.modules.base               import BaseModule
from src.utils              import Utils
from src.animation_utils    import start_animation
import threading
from textblob import TextBlob

class FeedbackAnalyzer(BaseModule):

    def run(self):
        login = input('login: ')
        
        try:
            done_event = threading.Event()
            loading_thread = start_animation(done_event)
            teams = Utils.get_evaluations_for_user(self.api, Utils.get_user_id(self.api, login), side='as_corrected')

        except Exception as e:
            return f'error: {e}'
        finally:
            done_event.set()
            loading_thread.join()
        
        comments = teams['comment']
        negative_comments = []
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
        return str(negative_comments)
