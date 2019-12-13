ALL_USERS_URI = "http://acs.amazonaws.com/groups/global/AllUsers"


def is_s3_object_is_public(s3_obj):
    # Loop over all the grants.
    for grant in s3_obj.Acl().grants:
        # Find the all users grantee.
        if "URI" not in grant["Grantee"]:
            continue
        elif grant["Grantee"]["URI"] == ALL_USERS_URI:
            if grant["Permission"] == "READ":
                return True
    return False
