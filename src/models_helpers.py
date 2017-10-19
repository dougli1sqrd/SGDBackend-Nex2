from src.models import DBSession, Base, Colleague, ColleagueLocus, ColleagueRelation, ColleagueReference, ColleagueUrl, Colleaguetriage, Dbentity, Locusdbentity, LocusAlias, Dnasequenceannotation, So, Locussummary, Phenotypeannotation, PhenotypeannotationCond, Phenotype, Goannotation, Go, Goslimannotation, Goslim, Apo, Straindbentity, Strainsummary, Reservedname, GoAlias, Goannotation, Referencedbentity, Referencedocument, Referenceauthor, ReferenceAlias, Chebi
from sqlalchemy import create_engine, and_
import os
import requests


class ModelsHelper(object):

    def get_all_colleague_data(self):
        """
        Get all colleague  data
        """
        all_colleagues = DBSession.query(Colleague).all()
        return all_colleagues

    def get_all_colleague_data_by_id(self, id):
        """
        Get all colleague associated data filter by colleague_id
        """
        colleague = DBSession.query(Colleague).filte(Colleague.colleague_id == id).first()
        return colleague

    def get_all_collegue_locus(self):
        """
        Get all colleague_locus data
        """
        colleague_loci = DBSession.query(ColleagueLocus).all()
        return colleague_loci

    def get_all_collegue_locus_by_id(self, id):
        """
        Get all colleague_locus data filter by colleague_id
        """
        colleague_locus = DBSession.query(ColleagueLocus).filter(ColleagueLocus.colleague_id == id).all()
        return colleague_locus

    def get_all_colleague_relation(self):
        """
        Get all colleague_relation data
        """
        colleague_relations = DBSession.query(ColleagueRelation).all()
        return colleague_relations

    def get_all_colleague_relation_by_id(self, id):
        """
        Get all colleague_relation data filter by colleague_id
        """
        colleague_relation = DBSession.query(ColleagueRelation).filter(ColleagueRelation.colleague_id == id).all()
        return colleague_relation

    def get_colleague_associated_data(self):
        """
        Get all colleague associated data(joins)
        """
        colleagues = self.get_all_colleague_data()
        loci = self.get_all_collegue_locus()
        relations = self.get_all_colleague_relation()
        result = self.association_helper(colleagues, loci, relations)
        return result




    def association_helper(self, colleagues, loci, relations):
        """
        Create colleague object from given lists
        """
        if len(colleagues) > 0:
            relation_obj = self.list_to_dict_colleague(relations)
            loci_obj = self.list_to_dict_colleague(loci)
            colleague_obj = {}
            for item in colleagues:
                if item.colleague_id not in colleague_obj:
                    colleague_obj[item.colleague_id] = {"loci": [], "relations": [], "colleagues": []}
                colleague_obj[item.colleague_id]['colleagues'].append(item)
                temp_loci = loci_obj.get(item.colleague_id)
                temp_relation = relation_obj.get(item.colleague_id)
                if temp_loci is not None:
                    colleague_obj[item.colleague_id]["loci"] = temp_loci
                if temp_relation is not None:
                    colleague_obj[item.colleague_id]["relations"] = temp_relation

            return colleague_obj


    def list_to_dict_colleague(self, lst):
        """
        Create dictionary given list of colleague objects
        """
        if len(lst) > 0:
            ids = list(set([x.colleague_id for x in lst]))
            if len(ids) > 0:
                dict_obj = {}
                for item in lst:
                    if item.colleague_id not in dict_obj:
                        dict_obj[item.colleague_id] = []
                    dict_obj[item.colleague_id].append(item)
                return dict_obj

    def get_colleague_data(self, colleague, dict_data):
        """
        Get Colleague data
        """
        _dict = {}
        _colleague = dict_data.get(colleague.colleague_id)
        if _colleague is not None:
            temp_relations = _colleague["relations"]
            temp_loci = _colleague["loci"]
            genes = []
            if _colleague:
                if len(_colleague["colleagues"]) > 0:
                    temp_coll = _colleague["colleagues"][0]
                    if temp_coll:
                        _dict["colleague_id"] = temp_coll.colleague_id
                        _dict["orcid"] = temp_coll.orcid
                        _dict["first_name"] = temp_coll.first_name
                        _dict["middle_name"] = temp_coll.middle_name
                        _dict["last_name"] = temp_coll.last_name
                        _dict["suffix"] = temp_coll.suffix
                        _dict["institution"] = temp_coll.institution
                        _dict["email"] = temp_coll.email
                        _dict["obj_url"] = temp_coll.obj_url
                        _dict["profession"] = temp_coll.profession
                        _dict["state"] = temp_coll.state
                        _dict["country"] = temp_coll.country
                        _dict["job_title"] = temp_coll.job_title
                        _dict["postal_code"] = temp_coll.postal_code
                        _dict["city"] = temp_coll.city
                        _dict["research_interest"] = temp_coll.research_interest
                        _dict["work_phone"] = temp_coll.work_phone
                        _dict["other_phone"] = temp_coll.other_phone
                if len(temp_loci) > 0:
                    genes = [x.locus.display_name for x in temp_loci]
                associates = self.get_associates_helper(temp_relations)
                if associates:
                    _dict["supervisors"] = associates["supervisors"]
                    _dict["lab_members"] = associates["members"]
            return _dict


    def get_associates_helper(self, relations_list):
        if len(relations_list) > 0:
            temp = filter(lambda item: item.association_type == "Associate",
                          relations_list)
            members = filter(
                lambda item: item.association_type != "Head of Lab", temp)
            supervisors = filter(
                lambda item: item.association_type == "Head of Lab",
                relations_list)
            if temp:
                return {"members": [x.associate.display_name for x in members], "supervisors": [x.associate.display_name for x in supervisors]}
            return None
