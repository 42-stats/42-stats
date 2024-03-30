from src.InterfaceResult import InterfaceResult
from src.modules.base import BaseModule
from src.utils import Utils, clear_terminal, prompt
from src.animation_utils import Animation
import threading
from textblob import TextBlob
from googletrans import Translator, LANGUAGES


class FeedbackAnalyzer(BaseModule):

    def translate_to_english(self, comments) -> list:
        loading_animation = Animation("Translating comments")
        translated_comments = []

        for comment in comments:
            if comment is None:
                continue
            try:
                detected = Translator.detect(comment)
                if LANGUAGES[detected.lang] != "en":
                    translated_comment = Translator.translate(comment, dest="en").text
                    translated_comments.append(translated_comment)
                else:
                    translated_comments.append(comment)
            except Exception as e:
                self.logs.error(f"\rtranslation error: {e}")
                translated_comments.append(comment)

        loading_animation.stop_animation()

        return translated_comments

    def run(self) -> str:
        print("\rwarning: shitty feature lol")
        print(
            "\rDo (very) basic language processing to list the negative comments you have received\n"
        )
        side = self.prompt(["as corrector?", "as corrected?"])
        login = prompt("\rlogin: ")
        side = side.replace(" ", "_")
        try:
            loading_animation = Animation(f"Fetching evaluation for user: {login}")
            teams = Utils.get_evaluations_for_user(
                self.api, Utils.get_user_id(self.api, login), side=side
            )
        except Exception as e:
            return f"error: {e}"
        finally:
            loading_animation.stop_animation()

        # comments = self.translate_to_english(teams['comment'])
        comments = teams["comment"]
        negative_comments = []
        loading_animation = Animation("Analyzing comments")
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
        loading_animation.stop_animation()
        formatted_negative_comments = "\n-\n".join(negative_comments)

        clear_terminal()
        print(
            f"{len(negative_comments)} negative comments found:\n-\n{formatted_negative_comments}"
        )

        return InterfaceResult.Success
