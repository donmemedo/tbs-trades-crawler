def filter_users_stage(trade_codes, from_gregorian_date, to_gregorian_date):
    return {
        "$match": {
            "$and": [
                {"TradeCode": {"$in": trade_codes}},
                {"TradeDate": {"$gte": from_gregorian_date}},
                {"TradeDate": {"$lte": to_gregorian_date}},
            ]
        }
    }


def project_commission_stage():
    return {
        "$project": {
            "Price": 1,
            "Volume": 1,
            "Total": {"$multiply": ["$Price", "$Volume"]},
            "PriorityAcceptance": 1,
            "BondDividend": 1,
            "TotalCommission": 1,
            "TradeItemBroker": 1,
            "TradeCode": 1,
            "Commission": {
                "$cond": {
                    "if": {"$eq": ["$TradeType", 1]},
                    "then": {
                        "$add": [
                            "$TotalCommission",
                            {"$multiply": ["$Price", "$Volume"]},
                        ]
                    },
                    "else": {
                        "$subtract": [
                            {"$multiply": ["$Price", "$Volume"]},
                            "$TotalCommission",
                        ]
                    },
                }
            },
        }
    }


def group_by_total_stage(_id):
    return {
        "$group": {
            "_id": _id,
            "TotalFee": {"$sum": "$TradeItemBroker"},
            "TotalPureVolume": {"$sum": "$Commission"},
            "TotalPriorityAcceptance": {"$sum": "$PriorityAcceptance"},
            "TotalBondDividend": {"$sum": "$BondDividend"},
        }
    }


def project_pure_stage():
    return {
        "$project": {
            "_id": 0,
            "TradeCode": "$_id",
            "TotalPureVolume": {
                "$add": [
                    "$TotalPriorityAcceptance",
                    "$TotalPureVolume",
                    "$TotalBondDividend",
                ]
            },
            "TotalFee": 1,
        }
    }


def join_customers_stage():
    return {
        "$lookup": {
            "from": "customers",
            "localField": "TradeCode",
            # "foreignField": "TradeCodes",
            "foreignField": "PAMCode",
            "as": "UserProfile",
        }
    }


def unwind_user_stage():
    return {"$unwind": "$UserProfile"}


def project_fields_stage():
    return {
        "$project": {
            "TradeCode": 1,
            "TotalFee": 1,
            "TotalPureVolume": 1,
            "FirstName": "$UserProfile.FirstName",
            "LastName": "$UserProfile.LastName",
            "Username": "$UserProfile.Username",
            "Mobile": "$UserProfile.Mobile",
            "RegisterDate": "$UserProfile.RegisterDate",
            "BankAccountNumber": "$UserProfile.BankAccountNumber",
            "FirmTitle": "$UserProfile.FirmTitle",
            "Telephone": "$UserProfile.Telephone",
            "FirmRegisterLocation": "$UserProfile.FirmRegisterLocation",
            "Email": "$UserProfile.Email",
            "ActivityField": "$UserProfile.ActivityField",
            "PartyTypeTitle": "$UserProfile.PartyTypeTitle",
            "BourseCodes": "$UserProfile.BourseCodes",
            "AccountCodes": "$UserProfile.AccountCodes",
            "RefererTitle": "$UserProfile.RefererTitle",
            "Phones": "$UserProfile.Phones",
            "BrokerBranchTitle": "$UserProfile.BrokerBranchTitle",
        }
    }


def sort_stage(sort_by, sort_order):
    return {"$sort": {sort_by: sort_order}}


def paginate_data(page, size):
    return {
        "$facet": {
            "metadata": [{"$count": "total"}],
            "items": [
                {"$skip": (page - 1) * size},
                {"$limit": size},
            ],
        }
    }


def unwind_metadata_stage():
    return {"$unwind": "$metadata"}


def project_total_stage():
    return {
        "$project": {
            "total": "$metadata.total",
            "items": 1,
        }
    }


def group_by_trade_code_stage():
    return {"$group": {"_id": "$TradeCode"}}


def project_by_trade_code_stage():
    return {"$project": {"_id": 0, "TradeCode": "$_id"}}


def match_inactive_users(inactive_users):
    return {"$match": {"PAMCode": {"$in": inactive_users}}}


def project_inactive_users():
    return {
        "$project": {
            "_id": 0,
            "TradeCode": 1,
            "FirstName": 1,
            "LastName": 1,
            "Username": 1,
            "Mobile": 1,
            "RegisterDate": 1,
            "BankAccountNumber": 1,
            "FirmTitle": 1,
            "Telephone": 1,
            "FirmRegisterDate": 1,
            "Email": 1,
            "ActivityField": 1,
        }
    }
