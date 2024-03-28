from src.modules.base import BaseModule
from src.utils import Utils
from src.animation_utils import Animation
from transformers import pipeline
from googletrans import Translator, LANGUAGES
import json


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
        side = self.prompt(["as corrector?", "as corrected?"]).replace(" ", "_")
        login = input("\rlogin: ")
        try:
            loading_animation = Animation(f"\rFetching evaluations for user: {login}")
            teams = Utils.get_evaluations_for_user(
                self.api, Utils.get_user_id(self.api, login), side=side
            )
        except Exception as e:
            return f"error: {e}"
        finally:
            loading_animation.stop_animation()

        negative_comments = []
        try:
            loading_animation = Animation(f"\rAnalyzing comments for user: {login}")
            sentiment_pipeline = pipeline(
                model="DT12the/distilbert-sentiment-analysis"
            )
            result = list(zip(sentiment_pipeline(list(teams["comment"])), teams["comment"]))
            with open("sentiments.json", "w") as sentiments_file:
                json.dump(result, sentiments_file, indent=4)
        except Exception as e:
            return f"error: {e}"
        finally:
            loading_animation.stop_animation()
        formatted_negative_comments = "\n-\n".join(negative_comments)
        return f"{len(negative_comments)} negative comments found:\n-\n{formatted_negative_comments}"
