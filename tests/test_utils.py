import unittest
from pi import type_check
class TestUtils(unittest.TestCase):
    def test_typeCheck(self):
        self.assertEqual(type_check("Hello",str),True)
        self.assertEqual(type_check([],list),True)
        self.assertEqual(type_check({},dict),True)
        self.assertEqual(type_check(1,int),True)
        self.assertEqual(type_check(3.14,float),True)
        self.assertEqual(type_check(u"Hello",unicode),True)
        self.assertEqual(type_check(True,bool),True)

        self.assertRaises(TypeError,type_check,"Hello",bool)
        self.assertRaises(TypeError,type_check,[],bool)
        self.assertRaises(TypeError,type_check,{},bool)
        self.assertRaises(TypeError,type_check,1,bool)
        self.assertRaises(TypeError,type_check,3.14,bool)
        self.assertRaises(TypeError,type_check,u"Hello",bool)
        self.assertRaises(TypeError,type_check,True,str)
