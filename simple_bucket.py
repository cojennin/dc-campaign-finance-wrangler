import boto


class SimpleBucket:
    def __init__(self, aws_access_key_id, aws_secret_access_key, bucket_name, delim="/"):
        #Sane defaults just in case.
        self.connection = boto.connect_s3(aws_access_key_id, aws_secret_access_key)
        self.bucket = self.connection.lookup(bucket_name)

        #A stricter exception woud be nice.
        if self.bucket is None:
            self.bucket = self.connection.create_bucket(bucket_name)


        self.delim = delim

    def save(self, key_list, contents):
        #Example output in S3 might look like dc-campaign-finance-ocf-data/csv/ofc_contributions.csv
        s3_obj = self.bucket.new_key(self.delim.join(key_list))

        #This could be a long running op, might be worthwhile to add a callback.
        s3_obj.set_contents_from_string(contents)