import csv
import re
import random
from natto import MeCab


class Ai:
    @staticmethod
    def robot_answer(input_text):
        import_text = ImportText('import.txt')
        fixed_phrase = FixedPhrase('pattern.csv')
        morpheme_analyzer = MorphemeAnalyzer()
        markov = Markov(morpheme_analyzer.analyze(import_text.read()))

        # ユーザー入力をインポートテキストに追記する
        if re.match('@|＠', input_text):
            add_text = re.sub('^@|^＠', '', input_text)
            import_text.add(add_text)
            markov.add(morpheme_analyzer.analyze(add_text))
            output_text = "覚えたよ！"
        else:
            # 定型文から回答を取得
            output_text = fixed_phrase.answer(input_text)

        # 定型文の回答がなければユーザー入力の名詞を起点にマルコフ連鎖で回答
        if output_text == "":
            nouns = morpheme_analyzer.extract_noun(input_text)
            output_text = markov.answer(nouns)

        if output_text == "":
            output_text = "ロボにも分かる言葉で言ってよぉ～"

        return output_text


class ImportText:
    def __init__(self, f_path):
        self.f_path = f_path

    def read(self):
        return open(self.f_path, 'r').read()

    def add(self, text):
        open(self.f_path, 'a').write(text + '\n')


class Markov:
    def __init__(self, words):
        self.words = words
        self.table = self.__build_table()

    def add(self, words):
        self.words += words
        self.table = self.__build_table()

    # ユーザー入力文からランダムに取得した形態素を起点に、マルコフ連鎖で回答文を生成
    def answer(self, user_morphemes):
        w1 = ''
        w2 = ''
        keys = list(self.table.keys())
        random.shuffle(keys)
        for key in keys:
            if key[0] in user_morphemes:
                w1 = key[0]
                w2 = key[1]
                break

        sentence = w1 + w2
        count = 0

        while w2 not in ["。", "！", "？", "!", "?", "."]:
            words = self.table.get((w1, w2))
            if words is None:
                break
            tmp = random.choice(words)
            sentence += tmp
            w1, w2 = w2, tmp
            count += 1
            if count > len(self.table):
                break
        return sentence

    def __build_table(self):
        table = {}
        w1 = ''
        w2 = ''
        for word in self.words:
            if w1 and w2:
                if (w1, w2) not in table:
                    table[(w1, w2)] = []
                table[(w1, w2)].append(word)
            w1, w2 = w2, word
        return table


class MorphemeAnalyzer:
    # 形態素解析
    @staticmethod
    def analyze(text):
        with MeCab('-Owakati') as nm:
            return nm.parse(text).split(" ")

    # 名詞のみ抽出
    @staticmethod
    def extract_noun(text):
        words = []
        with MeCab() as nm:
            for n in nm.parse(text, as_nodes=True):
                if not n.is_eos() and n.is_nor():
                    feature = n.feature.split(',', 1)
                    if '名詞' in feature:
                        words.append(n.surface)
        return words


class FixedPhrase:
    def __init__(self, f_path):
        self.f_path = f_path

    # ユーザー入力文が IN 列の文字列パターンにマッチしたら定型文を返す
    def answer(self, user_input_text):
        with open(self.f_path, 'r') as csv_f:
            csv_reader = csv.reader(csv_f)
            next(csv_reader, None)
            for row in csv_reader:
                while row.count('') > 0:
                    row.remove('')
                for w in row[1:]:
                    if re.match(w, user_input_text):
                        return row[0].format(IN=w)
        return ''


def output(text):
    print('ロボ: ' + text)


if __name__ == '__main__':
    output('ロボがいろいろ答えるよ')
    output('ロボに言葉を覚えさせたいときは@から初めてね！')

    while True:
        user_input = input('あなた: ')
        if user_input == '':
            continue
        if user_input == 'さようなら' or user_input == 'e':
            break

        output(Ai.robot_answer(user_input))

    output('ありがとう')
