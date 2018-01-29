import unittest
from pi import typeCheck
class TestUtils(unittest.TestCase):
    def test_typeCheck(self):
        self.assertEqual(typeCheck("Hello",str),True)
        self.assertEqual(typeCheck([],list),True)
        self.assertEqual(typeCheck({},dict),True)
        self.assertEqual(typeCheck(1,int),True)
        self.assertEqual(typeCheck(3.14,float),True)
        self.assertEqual(typeCheck(u"Hello",unicode),True)
        self.assertEqual(typeCheck(True,bool),True)
        
        self.assertRaises(TypeError,typeCheck,"Hello",bool)
        self.assertRaises(TypeError,typeCheck,[],bool)
        self.assertRaises(TypeError,typeCheck,{},bool)
        self.assertRaises(TypeError,typeCheck,1,bool)
        self.assertRaises(TypeError,typeCheck,3.14,bool)
        self.assertRaises(TypeError,typeCheck,u"Hello",bool)
        self.assertRaises(TypeError,typeCheck,True,str)
