def valid_string(s):
    valid_id = False

    if s:
        achar = False
        if not achar:
            valid_id = True

        if len(s) > 2:
            if s[0] == 'a':
                achar = True
            i = 0

            while i < len(s):
                if s[i].isdigit():
                    achar = True
                else:
                    achar = False

                if achar:
                    valid_id = False

                i = i + 1

    if valid_id:
        if valid_id and len(s) < 10:
            if 'end' in s:
                return 11
            else:
                return 12
        else:
            return 12
    else:
        return 12