import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.gridlayout import GridLayout

import docx
import string
import nltk
from nltk.corpus import stopwords
from natasha import (
    Segmenter,
    MorphVocab,
    
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
    
    PER,
    NamesExtractor,

    Doc
)

class dictionaries:
    def __init__(self): 
        self.diction = []
        self.LoadDictionory()

    def SaveDictionary(self): #сохранение словаря в файл
        file = open('narkotiki.txt','w')
        for i in self.diction:
            line = i[0]+'#'
            for j in i[1]:
                line += j+'#'
            line+='\n'
            file.write(line)
        file.close()

    def LoadDictionory(self): #загрузка словаря из файля в систему
        file = open('narkotiki.txt','r')
        filesdata = file.readlines()
        for i in filesdata:
            line = i.split('#')
            self.AddDict(line[0],line[1:-1])
        file.close()

    def AddDict(self,name,dict=[]): #добавление словаря
        if type(dict) != list:
            self.diction.append([name,[dict]])
        else:
            self.diction.append([name,dict])

    def AddWords(self,numb,words): #добавление слова/слов в словарь
        self.diction[numb][1].extend(words)

    def Show(self): #вывод словарей
        for i in self.diction:
            print("Словарь",i[0],":", i[1])

def analis(txt): #анализ текста (процентное соотношение)
    res=''
    numb = len(dictionary.diction)
    NumbOfWords = len(txt.split())
    for i in range (numb):
        coun = 0
        for j in dictionary.diction[i][1]:
            coun += txt.count(j)
        res+='Процентное соотношение по словарю '+str(dictionary.diction[i][0])+':'+str(coun/NumbOfWords*100)+'%\n'
    return res

def normal(txt):
    doc=Doc(txt)
    doc.segment(segmenter) #разбивает на токены(слова, знаки припинания)
    doc.tag_morph(morph_tagger) #определяет часть речи
    for token in doc.tokens:    #приводит всё к начальной форме(слова, знаки и прочее)
        token.lemmatize(morph_vocab)

    doc.parse_syntax(syntax_parser)  #определяет связи
    doc.tag_ner(ner_tagger)  #извлечение сущностей
    for span in doc.spans:   #нормализация сущностей
            span.normalize(morph_vocab)

    text_new = ''    
    stop = stopwords.words("russian")
    rubbish = string.punctuation + '—' + '«' + '»'
    for _ in doc.tokens:                             #вывод слов без мусора
        if _.lemma in rubbish or _.lemma in stop or  _.lemma.isdigit():
            continue
        text_new += ' ' + _.lemma
    return text_new



class Page(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.add_widget(Label(
            text='Введите текст или загрузите',
            size_hint=(.001,.001),
            pos_hint={'x':.5,'y':.9}))

        self.textbar=TextInput(
            multiline=True,
            size_hint=(.8,.5),
            pos_hint={'x':.1,'y':.37})
        self.textbar.text='Текст'
        self.add_widget(self.textbar)

        self.butt1=Button(text="Анализ")
        self.butt1.size_hint=(.1,.01)
        self.butt1.pos_hint={'x':.1,'y':.1}
        self.butt1.bind(on_press=self.Analis)
        self.add_widget(self.butt1)

        self.butt2=Button(text="Файл")
        self.butt2.size_hint=(.1,.01)
        self.butt2.pos_hint={'x':.8,'y':.1}
        self.butt2.bind(on_press=self.FileChoose)
        self.add_widget(self.butt2)

        self.add_widget(Label(
            text='Результат:',
            size_hint=(0.001,0.001),
            pos_hint={'x':.4,'y':.3}))

        self.result=TextInput(multiline=True)
        self.result.readonly=True
        self.result.size_hint=(.55,.2)
        self.result.pos_hint={'x':.23,'y':.05}
        self.add_widget(self.result)

    def Analis(self,instance):
        self.result.text=analis(normal(self.textbar.text))

    def FileChoose(self, instance):
        self.lay=FileChooserLay()
        self.popup=FileChooser(content=self.lay)
        self.popup.open()
        self.lay.ids.butcl.bind(on_press=self.popup.dismiss)
        self.lay.ids.butop.bind(on_press=self.opendoc)

    def opendoc(self, instance):
        text=''
        try:
            fileDoc = docx.Document(self.lay.ids.file_chooser.selection[0]) #загрузка текста из вордовского документа в систему
            for paragraph in fileDoc.paragraphs:
                text+=paragraph.text+'\n'
            self.textbar.text=text
            self.popup.dismiss()
        except:
            pass

class FileChooser(Popup):
    pass

class FileChooserLay(FloatLayout):
    pass
        

class AnalisApp(App):
    def build(self):
        self.load_kv('AnalizeTextsKivy.kv')
        return Page()

if __name__ == "__main__":
    dictionary = dictionaries()

    nltk.download('stopwords')

    segmenter = Segmenter()
    morph_vocab = MorphVocab()

    emb = NewsEmbedding()
    morph_tagger = NewsMorphTagger(emb)
    syntax_parser = NewsSyntaxParser(emb)
    ner_tagger = NewsNERTagger(emb)

    names_extractor = NamesExtractor(morph_vocab)

    AnalisApp().run()