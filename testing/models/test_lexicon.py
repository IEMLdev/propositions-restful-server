from ieml.ieml_objects.tools import RandomPoolIEMLObjectGenerator
from ieml.usl.tools import usl
from models.commons import generate_translations
from testing.models.stub_db import ModelTestCase


class TestModel(ModelTestCase):
    connectors = ('lexicon', 'library')

    def test_new(self):
        id = self.lexicon.add_lexicon("test")
        self.assertEqual(id, self.lexicon.get(name='test')['id'])

        self.assertTrue(self.lexicon.remove_lexicon(id=id))

    def test_add_words(self):
        id = self.lexicon.add_lexicon("test")

        words = [str(RandomPoolIEMLObjectGenerator().word()) for _ in range(10)]

        with self.assertRaises(ValueError):
            self.lexicon.add_words(words, id)

        for w in words:
            u = usl(w)
            self.library.save(u, generate_translations(u))

        self.assertTrue(self.lexicon.add_words(words, id))

        g = self.lexicon.get(id=id)
        self.assertSetEqual(set(w['USL']['IEML'] for w in g['words']), set(map(str, words)))

        self.assertTrue(self.lexicon.remove_words(words, id))

    def test_all_lexicons(self):
        names = ["test%d"%i for i in range(10)]
        ids = [self.lexicon.add_lexicon(n) for n in names]

        lexicons = self.lexicon.all_lexicons()

        self.assertTrue(all(g['nb_words'] == 0 for g in lexicons))
        self.assertSetEqual(set(names), set(g['name'] for g in lexicons))
        self.assertSetEqual(set(ids), set(g['id'] for g in lexicons))

    def test_double_creation(self):
        self.lexicon.drop()
        self.lexicon.add_lexicon("test")
        with self.assertRaises(ValueError):
            self.lexicon.add_lexicon("test")

    def test_favorite(self):
        for name in range(10):
            self.lexicon.add_lexicon(str(name))

        self.lexicon.set_favorites(list(map(str, range(0, 10,2))))

        self.assertListEqual([int(k['name']) for k in self.lexicon.all_lexicons(favorite=True)],
                             list(range(0, 10,2)))

        self.assertTrue(all(int(k['name']) not in list(range(0, 10,2)) for k in self.lexicon.all_lexicons(favorite=False)))
