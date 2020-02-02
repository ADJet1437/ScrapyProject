from __future__ import division

def hash_str_2_int(org_str):
    """
    convert unique string_type_source_internal_id to
    unique int_type_id

    i.e. 
    convert string like
    'nVvLEkD2ZoEqhzir7T5qGJ'
    to a 10-digit number

    hash logic:
    manipulate the string using the ascii number for each char.
    taking index in to consideration and increasing the weight of index,
    so that the order of char will be more important
    to reduce the possibilies of a repeat source_id.

    This function should guarantee the uniqueness and consistance
    of the original source internal id.
    """
    org_nums =  [int(ord(org_char)) for org_char in org_str]
    hashed_int = 0
    # place holder for index 0 so that we don't ignore the first char
    org_nums.insert(0, 0)

    for ind, x in enumerate(org_nums):
        hashed_int += (-(-x//2))*ind*x**2 + ind**10
    return (hashed_int ** 3) % (10)

if __name__ == '__main__':
    test_strs = [u'o5HBA3WzCkzCRSYrwRRdGP', u'4osbkWa29re6Wiv5LK7mkM',
                 u'mHW8rDXDHQX7gbzhYrKQk8', u'm3Mz5ejeoGHB9g2kjNi9j', 
                 u'KGisqYnRRDqc6odfJqM9RX', u'vJ7BYDaYG6fMT7nrc2Wnt3', 
                 u'cHoC2EpjtPpBQviaxsoy9o', u'wEFCF68dzhwFz3ht4qFqPM', 
                 u'NeyuwwZ8gz4vWg7CjsDMCk', u'7xmpYuRf87Z9dmkJNUeQ4o', 
                 u'qLyRqd2U9QQrAipZUewxvT', u'jM3J4wuksc5sobRnYMDwri', 
                 u'NkBwELSfxfGCV4AbfBEheW', u'HG5DCiarvDuJDBuk93CoJd', 
                 u'vKGdVYioeA67RLXf5QrgmE', u'ERjBMrFcc27HcQjCvFGJHW', 
                 u'TyuyhHQsVuyN6Tm39jENkh', u'WWTCRyNi9z7rLTwqpuXsXg',
                 u'DPPiPF8C6bUqmQaTXhbU2n', u'XWnoqxTiKzYtgsMXqMezoh',
                 u'PibJg3CGzcTH2PJHZ7PCBk', u'MhG4TjHBNELaT8fioCLydn', 
                 u'bMKPFwanRppZ2uRucYPVU3', u'573dGrw8Lh4cyMFmhcbaYY', 
                 u'kx3WzfjgiiGPyjFwkWwt7B', u'72vYdvA5xNsmGkpBMR6XqB', 
                 u'tE5u5k4fXXhKaoGR8oJbLR', u'eEVnodMYkKin4ycRpzbn7T', 
                 u'pBdo957q3yMcAPiVqwxQzi', u'U2V6f4Ee8LBCDEr4EJtFGP', 
                 u'BykCTE3R9dN6XcRp3pzDUR', u'p5iHSwGXHTmqFsgnyFwKt5', 
                 u'miY8a6qvju8BRQQs7tLAc3', u'RdD6bocngZMKbQx2GNWMQA',
                 u'jfQhx4RfZuxD77xjJJZsmW', u'CvT74k28bLKcY5mZwbnMnk', 
                 u'stxyxTgkA3ghKMeUCUCMdH', u'X4jFq6xsuxuibfUvF6u5KD',
                 u'qsKBTBUdMHUXmoRdt8nVpb', u'ccttqCxhVsqJ9hKBnR7Xcb', 
                 u'Qjz7mAkAToDeD73Y8Kex7G', u'6qryADJnP9oaACQPjjhCsh', 
                 u'qFB4XruZmdaFWzguwnEACP', u'SfFLo68orDcNLNTanmA6Ce', 
                 u'yzZ6CGEEFdmz3uWpAh4TCk', u'JUQHuGiHGp5DcovcoGkqjH', 
                 u'9nRCaibS6capSZwdhpHiET', u'bMFKkWHgQUT8pbNCv5G2R7', 
                 u'ZJCqPrtaxCHT9dEKXsuULR', u'oAFkVs94pthH7dtdngat9D', 
                 u'a7kZJy2pM5WXXvKwobNvEY', u'wSEXiPkNE4GBngEMchhYQ9', 
                 u'NUoFxfM2yXbzZJebVejL8d', u'V2S3FnkbyiVFgnQ9YrPmt5', 
                 u'frZhVJiUJMQUSBMpYdS3LB', u'JcTWCR9DvamogGjzrfE6c', 
                 u'tdpDuMK9j65wtLQM77K5sF', u'Eb9TWwnBDGkHkC4Bpmetvm', 
                 u'mTq7EGiCWYADTY2AEF6pL6', u'j73HKwbvgrcjDNGutcM5km', 
                 u'uEzgU9C8aDTSXQjJrRNe26', u'NAQAvxcpSC2Tt8oZHRMfPE', 
                 u'KfwFAdwUXvfkvnzBi24UZM', u'xjXgxH6FVF8fzqnqFsiKK6', 
                 u'qpQM8XfumzWhJFhs9P8DN6', u'sceDESL3orTvq5HVet7KJY', 
                 u'ZK7pcGxALgj43Q3wtzXuiH', u'kKpL7YG7o4f29vGJwWLu2g', 
                 u'pgtKg6qRmsCPVeyyVYqB8d', u'Z6E72Lmgu4obJCGmkUM9Gi']
    sum_test = len(test_strs)
    sum_pass = 0
    sum_fail = 0

    for test_str in test_strs:
        id_1 = hash_str_2_int(test_str)
        id_2 = hash_str_2_int(test_str)
        if id_1 == id_2:
            print('>>> Passed >>>')
            sum_pass +=1
        else:
            print('>>> Failed >>>')
            print('id1: {}').format(id_1)
            print('id2: {}').format(id_2)
            sum_fail +=1

    print('Total: {} passed, {} failed out of {}').format(sum_pass, sum_fail, sum_test)
