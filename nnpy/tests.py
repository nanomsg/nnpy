from __future__ import print_function
import nnpy, unittest

class Tests(unittest.TestCase):
    def test_basic(self):

        pub = nnpy.Socket(nnpy.AF_SP, nnpy.PUB)
        pub.bind('inproc://foo')
        self.assertEqual(pub.getsockopt(nnpy.SOL_SOCKET, nnpy.DOMAIN), 1)

        sub = nnpy.Socket(nnpy.AF_SP, nnpy.SUB)
        sub.connect('inproc://foo')
        sub.setsockopt(nnpy.SUB, nnpy.SUB_SUBSCRIBE, '')

        pub.send('FLUB')
        poller = nnpy.PollSet((sub, nnpy.POLLIN))
        self.assertEqual(poller.poll(), 1)
        self.assertEqual(sub.recv(), 'FLUB')
        self.assertEqual(pub.get_statistic(nnpy.STAT_MESSAGES_SENT), 1)

def suite():
    return unittest.makeSuite(Tests)

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
