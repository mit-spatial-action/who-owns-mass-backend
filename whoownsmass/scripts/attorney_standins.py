import re
import csv
import string
from django.db.models.functions import Length
from who_owns.models import Docket, Filing, Plaintiff, Defendant, Attorney

dockets = (
    Docket.objects.filter(text__contains="Attorney Appearance")
    .annotate(text_len=Length("text"))
    .filter(text_len__gt=len("Attorney Appearance"))
)


def run_extraction():
    failures = 0
    successes = 0
    attorney_hits = 0
    attorney_exists = 0
    with open("results.csv", "a+") as f:
        fieldnames = [
            "docket_id",
            "text",
            "action",
            "new_attorney_type",
            "new_attorney",
            "new_attorney_bar",
            "p_name",
            "ptf_bar",
            "d_name",
            "def_bar",
            "client",
        ]
        csvwriter = csv.DictWriter(f, fieldnames=fieldnames)
        csvwriter.writeheader()
        for docket in dockets:
            res = get_attorney_and_client_from_str(docket.text)
            if res == (None, None, None, None):
                failures += 1
            else:
                filing = Filing.objects.get(docket_id=docket.docket_id)
                plaintiffs = Plaintiff.objects.filter(
                    docket=docket.docket_id
                ).values_list("name")
                defendants = Defendant.objects.filter(
                    docket=docket.docket_id
                ).values_list("name")

                attorney_type, defendant, plaintiff, new_attorney, new_attorney_bar = (
                    None,
                    None,
                    None,
                    None,
                    None,
                )

                # figure out if it's on the plaintiff or defendant side
                if not res[3]:
                    if res[1]:
                        for ptf in plaintiffs:
                            if res[1] == ptf[0]:
                                attorney_type = "ptf"
                                plaintiff = ptf[0]
                                break
                        if not attorney_type:
                            for defe in defendants:
                                if res[1] == defe[0]:
                                    attorney_type = "def"
                                    defendant = defe[0]
                                    break

                elif res[3] == "ptf":
                    attorney_type = res[3]
                    for ptf in plaintiffs:
                        if res[1] == ptf[0]:
                            attorney_type = "ptf"
                            plaintiff = ptf
                            break
                elif res[3] == "def":
                    attorney_type = res[3]
                    for defe in defendants:
                        if res[1] == defe[0]:
                            attorney_type = "def"
                            defendant = defe
                            break
                if res[0]:
                    attorney_exists += 1
                    new_attorney = res[0]
                    attorneys = Attorneys.objects.filter(name=res[0])
                    if len(attorneys) == 1:
                        attorney_hits += 1
                        new_attorney_bar = attorneys.first().bar

                row = {
                    "docket_id": docket.docket_id,
                    "text": docket.text,
                    "action": res[2],
                    "ptf_bar": filing.ptf_attorney_id,
                    "def_bar": filing.def_attorney_id,
                    "d_name": defendant,
                    "p_name": plaintiff,
                    "new_attorney_type": attorney_type,
                    "new_attorney": new_attorney,
                    "new_attorney_bar": new_attorney_bar,
                }
                csvwriter.writerow(row)
                successes += 1
    return {
        "failures": failures,
        "successes": successes,
        "attorney_hits": attorney_hits,
        "attorney_exists": attorney_exists,
    }


def get_attorney_and_client_from_str(input_str):
    """
    >>> get_attorney_and_client_from_str('Attorney Appearance | On this date 12/11/2019 Pro Se added for Example, Bob')
    ('Pro Se', 'Example, Bob', 'added', None)
    >>> get_attorney_and_client_from_str('Attorney Appearance | On this date 12/03/2019 Ashton, Esq., Donna M added for Longview Apartments at Georgetown, LLC')
    ('Ashton Donna M', 'Longview Apartments at Georgetown, LLC', 'added', None)
    >>> get_attorney_and_client_from_str('On this date Judrick K Fletcher, Esq. added as Limited Assistance Representation for Defendant Elvin Cochran')
    ('Judrick K Fletcher', 'Elvin Cochran', 'added', 'def')
    >>> get_attorney_and_client_from_str('Attorney Appearance | On this date Pro Se dismissed/withdrawn for Defendant Elvin Cochran')
    ('Pro Se', 'Elvin Cochran', 'dismissed', 'def')
    >>> get_attorney_and_client_from_str('Attorney Appearance for Defendant by K. Wibby, Esq.')
    """
    try:
        try:
            _, parties = re.split(
                r"(?:On this date)(?:\s*)?(?:\d{2}\/\d{2}\/\d{4})?\s*", input_str
            )
        except:
            parties = input_str
        attorney, action, client = re.split(
            r"(?:\s*)(added as| added for|withdrawn for|dismissed for|dismissed\/withdrawn for|dismissed\/withdrawn as|withdrawn as)(?:\s*)",
            parties,
        )
        action = action.lower()
        if ("dismissed" in action) or ("withdrawn" in action):
            action = "dismissed"
        elif "added" in action:
            action = "added"
        attorney_type = None
        if "Defendant" in client:
            client = client.split("Defendant")[-1].strip()
            attorney_type = "def"
        elif "Plaintiff" in client:
            client = client.split("Plaintiff")[-1].strip()
            attorney_type = "ptf"
        if "Esq." in attorney:
            attorney = attorney.translate(str.maketrans("", "", string.punctuation))
            attorney = "".join(attorney.split(" Esq"))
        return (attorney, client, action, attorney_type)
    except Exception as err:
        print("Exception", input_str)
        return (None, None, None, None)
