from src.InterfaceResult import InterfaceResult
from src.Spinner import Spinner
from src.modules.base import BaseModule
from src.utils import Utils, clear_terminal, prompt, prompt_select
from textblob import TextBlob
from googletrans import Translator, LANGUAGES


class FeedbackAnalyzer(BaseModule):
    """
    Analyzes feedback comments and performs basic language processing to list negative comments.

    Attributes:
        api: The API object used for fetching evaluations.
    """

    @Spinner("Translating comments")
    def translate_to_english(self, comments) -> list:
        """
        Translates comments to English.

        Args:
            comments: A list of comments to be translated.

        Returns:
            A list of translated comments.
        """
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

        return translated_comments

    def run(self) -> str:
        """
        Runs the feedback analysis.

        Returns:
            A string indicating the result of the analysis.
        """
        print("\rwarning: shitty feature lol")
        print(
            "\rDo (very) basic language processing to list the negative comments you have received\n"
        )
        side = prompt_select(["as corrector?", "as corrected?"])
        login = prompt("\rlogin: ")
        side = side.replace(" ", "_")

        with Spinner(f"Fetching evaluation for user: {login}") as spinner:
            try:
                teams = Utils.get_evaluations_for_user(
                    self.api,
                    Utils.get_user_id(self.api, login),
                    side=side,
                    spinner=spinner,
                )
            except Exception as e:
                return f"error: {e}"

        # comments = self.translate_to_english(teams['comment'])
        comments = teams["comment"]
        negative_comments = []
        with Spinner("Analyzing comments"):
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

        formatted_negative_comments = "\n-\n".join(negative_comments)

        clear_terminal()
        print(
            f"{len(negative_comments)} negative comments found:\n-\n{formatted_negative_comments}"
        )

        return InterfaceResult.Success
