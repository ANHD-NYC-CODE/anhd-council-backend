# Dataset Field Audit Report

*Generated: 2026-04-04*

## Executive Summary

### 1. Always-NULL fields displayed by frontend (BROKEN): 6

| Table | Field | Frontend Usage |
|-------|-------|----------------|
| `datasets_foreclosure` | `mortgage_amount` | Table column (Mortgage Amount), dollarFormatter |
| `datasets_property` | `overlay2` | Zoning section |
| `datasets_property` | `spdist2` | Zoning section |
| `datasets_property` | `spdist3` | Zoning section |
| `datasets_property` | `zonedist3` | Zoning section |
| `datasets_property` | `zonedist4` | Zoning section |

### 2. Always-NULL fields not used by frontend (removable): 74

| Table | Field |
|-------|-------|
| `datasets_conhrecord` | `aeporder` |
| `datasets_conhrecord` | `censustract` |
| `datasets_conhrecord` | `ntaneighborhoodtabulationarea` |
| `datasets_coresubsidyrecord` | `serviolation2017` |
| `datasets_coresubsidyrecord` | `serviolation2018` |
| `datasets_coresubsidyrecord` | `serviolation2019` |
| `datasets_coresubsidyrecord` | `taxdelinquency2016` |
| `datasets_coresubsidyrecord` | `taxdelinquency2018` |
| `datasets_coresubsidyrecord` | `taxdelinquency2019` |
| `datasets_ecbviolation` | `infractioncode10` |
| `datasets_ecbviolation` | `infractioncode8` |
| `datasets_ecbviolation` | `infractioncode9` |
| `datasets_ecbviolation` | `sectionlawdescription10` |
| `datasets_ecbviolation` | `sectionlawdescription8` |
| `datasets_ecbviolation` | `sectionlawdescription9` |
| `datasets_eviction` | `evictionzip` |
| `datasets_eviction` | `geosearch_address` |
| `datasets_eviction` | `schedulestatus` |
| `datasets_lispenden` | `thirdparty` |
| `datasets_ocahousingcourt` | `bin` |
| `datasets_ocahousingcourt` | `boroughcode` |
| `datasets_ocahousingcourt` | `dateofjurydemand` |
| `datasets_ocahousingcourt` | `hnum` |
| `datasets_ocahousingcourt` | `housenumber` |
| `datasets_ocahousingcourt` | `lat` |
| `datasets_ocahousingcourt` | `lng` |
| `datasets_ocahousingcourt` | `lon` |
| `datasets_ocahousingcourt` | `placename` |
| `datasets_ocahousingcourt` | `sname` |
| `datasets_ocahousingcourt` | `street1` |
| `datasets_ocahousingcourt` | `street2` |
| `datasets_ocahousingcourt` | `streetname` |
| `datasets_property` | `mapplutof` |
| `datasets_property` | `masdate` |
| `datasets_property` | `newnotinold` |
| `datasets_property` | `notes` |
| `datasets_property` | `polidate` |
| `datasets_psforeclosure` | `bldgareasqft` |
| `datasets_pspreforeclosure` | `bldgareasqft` |
| `datasets_pspreforeclosure` | `mortgageamount` |
| `datasets_rentstabilizationrecord` | `abat2007` |
| `datasets_rentstabilizationrecord` | `abat2008` |
| `datasets_rentstabilizationrecord` | `abat2018` |
| `datasets_rentstabilizationrecord` | `abat2019` |
| `datasets_rentstabilizationrecord` | `abat2020` |
| `datasets_rentstabilizationrecord` | `abat2021` |
| `datasets_rentstabilizationrecord` | `abat2022` |
| `datasets_rentstabilizationrecord` | `abat2023` |
| `datasets_rentstabilizationrecord` | `abat2024` |
| `datasets_rentstabilizationrecord` | `dhcr2007` |
| `datasets_rentstabilizationrecord` | `dhcr2008` |
| `datasets_rentstabilizationrecord` | `dhcr2010` |
| `datasets_rentstabilizationrecord` | `dhcr2014` |
| `datasets_rentstabilizationrecord` | `dhcr2015` |
| `datasets_rentstabilizationrecord` | `dhcr2016` |
| `datasets_rentstabilizationrecord` | `dhcr2017` |
| `datasets_rentstabilizationrecord` | `dhcr2018` |
| `datasets_rentstabilizationrecord` | `dhcr2019` |
| `datasets_rentstabilizationrecord` | `dhcr2020` |
| `datasets_rentstabilizationrecord` | `dhcr2021` |
| `datasets_rentstabilizationrecord` | `dhcr2022` |
| `datasets_rentstabilizationrecord` | `dhcr2023` |
| `datasets_rentstabilizationrecord` | `dhcr2024` |
| `datasets_rentstabilizationrecord` | `est2018` |
| `datasets_rentstabilizationrecord` | `est2019` |
| `datasets_rentstabilizationrecord` | `est2020` |
| `datasets_rentstabilizationrecord` | `est2021` |
| `datasets_rentstabilizationrecord` | `est2022` |
| `datasets_rentstabilizationrecord` | `est2023` |
| `datasets_rentstabilizationrecord` | `est2024` |
| `datasets_rentstabilizationrecord` | `uc2024` |
| `datasets_rentstabilizationrecord` | `uc2025` |
| `datasets_rentstabilizationrecord` | `uc2026` |
| `datasets_rentstabilizationrecord` | `uc2027` |

### 3. Populated fields not used by frontend (unused data): 639

| Table | Field | Populated % |
|-------|-------|-------------|
| `datasets_acrisreallegal` | `airrights` | 100.0% |
| `datasets_acrisreallegal` | `bbl` | 100.0% |
| `datasets_acrisreallegal` | `block` | 100.0% |
| `datasets_acrisreallegal` | `borough` | 100.0% |
| `datasets_acrisreallegal` | `documentid` | 100.0% |
| `datasets_acrisreallegal` | `easement` | 100.0% |
| `datasets_acrisreallegal` | `goodthroughdate` | 100.0% |
| `datasets_acrisreallegal` | `key` | 100.0% |
| `datasets_acrisreallegal` | `lot` | 100.0% |
| `datasets_acrisreallegal` | `partiallot` | 100.0% |
| `datasets_acrisreallegal` | `propertytype` | 100.0% |
| `datasets_acrisreallegal` | `recordtype` | 100.0% |
| `datasets_acrisreallegal` | `streetname` | 71.8% |
| `datasets_acrisreallegal` | `streetnumber` | 71.3% |
| `datasets_acrisreallegal` | `subterraneanrights` | 100.0% |
| `datasets_acrisreallegal` | `unit` | 22.4% |
| `datasets_acrisrealmaster` | `borough` | 100.0% |
| `datasets_acrisrealmaster` | `crfn` | 53.8% |
| `datasets_acrisrealmaster` | `goodthroughdate` | 100.0% |
| `datasets_acrisrealmaster` | `modifieddate` | 100.0% |
| `datasets_acrisrealmaster` | `pcttransferred` | 100.0% |
| `datasets_acrisrealmaster` | `recordtype` | 100.0% |
| `datasets_acrisrealmaster` | `reelnbr` | 100.0% |
| `datasets_acrisrealmaster` | `reelpage` | 100.0% |
| `datasets_acrisrealmaster` | `reelyear` | 100.0% |
| `datasets_acrisrealparty` | `goodthroughdate` | 100.0% |
| `datasets_acrisrealparty` | `recordtype` | 100.0% |
| `datasets_aepbuilding` | `aepround` | 100.0% |
| `datasets_aepbuilding` | `aepstartdate` | 100.0% |
| `datasets_aepbuilding` | `bbl` | 99.8% |
| `datasets_aepbuilding` | `bin` | 99.8% |
| `datasets_aepbuilding` | `borough` | 100.0% |
| `datasets_aepbuilding` | `buildingid` | 100.0% |
| `datasets_aepbuilding` | `censustract` | 99.9% |
| `datasets_aepbuilding` | `communityboard` | 99.9% |
| `datasets_aepbuilding` | `councildistrict` | 99.9% |
| `datasets_aepbuilding` | `currentstatus` | 100.0% |
| `datasets_aepbuilding` | `dischargedate` | 75.9% |
| `datasets_aepbuilding` | `latitude` | 99.9% |
| `datasets_aepbuilding` | `longitude` | 99.9% |
| `datasets_aepbuilding` | `nta` | 99.9% |
| `datasets_aepbuilding` | `number` | 100.0% |
| `datasets_aepbuilding` | `ofbcviolationsatstart` | 100.0% |
| `datasets_aepbuilding` | `postcode` | 99.9% |
| `datasets_aepbuilding` | `street` | 100.0% |
| `datasets_aepbuilding` | `totalunits` | 100.0% |
| `datasets_conhrecord` | `bbl` | 100.0% |
| `datasets_conhrecord` | `bin` | 100.0% |
| `datasets_conhrecord` | `block` | 100.0% |
| `datasets_conhrecord` | `borocode` | 100.0% |
| `datasets_conhrecord` | `borough` | 100.0% |
| `datasets_conhrecord` | `bqi` | 100.0% |
| `datasets_conhrecord` | `buildingid` | 100.0% |
| `datasets_conhrecord` | `censustract2020` | 100.0% |
| `datasets_conhrecord` | `communityboard` | 100.0% |
| `datasets_conhrecord` | `councildistrict` | 100.0% |
| `datasets_conhrecord` | `dateadded` | 100.0% |
| `datasets_conhrecord` | `discharged7a` | 100.0% |
| `datasets_conhrecord` | `dischargedaep` | 100.0% |
| `datasets_conhrecord` | `dobvacateorder` | 100.0% |
| `datasets_conhrecord` | `harassmentfinding` | 100.0% |
| `datasets_conhrecord` | `hpdvacateorder` | 100.0% |
| `datasets_conhrecord` | `latitude` | 100.0% |
| `datasets_conhrecord` | `longitude` | 100.0% |
| `datasets_conhrecord` | `lot` | 100.0% |
| `datasets_conhrecord` | `neighborhoodtabulationareanta2020` | 100.0% |
| `datasets_conhrecord` | `postcode` | 100.0% |
| `datasets_conhrecord` | `streetaddress` | 100.0% |
| `datasets_coresubsidyrecord` | `agencyname` | 100.0% |
| `datasets_coresubsidyrecord` | `agencysuppliedid1` | 53.1% |
| `datasets_coresubsidyrecord` | `agencysuppliedid2` | 18.4% |
| `datasets_coresubsidyrecord` | `assessedvalue` | 100.0% |
| `datasets_coresubsidyrecord` | `bbl` | 100.0% |
| `datasets_coresubsidyrecord` | `boroname` | 100.0% |
| `datasets_coresubsidyrecord` | `buildings` | 99.7% |
| `datasets_coresubsidyrecord` | `ccdid` | 100.0% |
| `datasets_coresubsidyrecord` | `ccdname` | 100.0% |
| `datasets_coresubsidyrecord` | `cdid` | 100.0% |
| `datasets_coresubsidyrecord` | `cdname` | 99.9% |
| `datasets_coresubsidyrecord` | `dataoutputdate` | 100.0% |
| `datasets_coresubsidyrecord` | `enddate` | 66.4% |
| `datasets_coresubsidyrecord` | `fcsubsidyid` | 100.0% |
| `datasets_coresubsidyrecord` | `latitude` | 96.3% |
| `datasets_coresubsidyrecord` | `longitude` | 96.3% |
| `datasets_coresubsidyrecord` | `ownername` | 100.0% |
| `datasets_coresubsidyrecord` | `preservation` | 63.1% |
| `datasets_coresubsidyrecord` | `programname` | 100.0% |
| `datasets_coresubsidyrecord` | `projectname` | 51.4% |
| `datasets_coresubsidyrecord` | `pumaid` | 99.9% |
| `datasets_coresubsidyrecord` | `pumaname` | 99.9% |
| `datasets_coresubsidyrecord` | `reacdate` | 0.1% |
| `datasets_coresubsidyrecord` | `reacscore` | 3.7% |
| `datasets_coresubsidyrecord` | `regulatorytool` | 100.0% |
| `datasets_coresubsidyrecord` | `resunits` | 98.7% |
| `datasets_coresubsidyrecord` | `serviolation2021` | 41.0% |
| `datasets_coresubsidyrecord` | `standardaddress` | 99.9% |
| `datasets_coresubsidyrecord` | `startdate` | 98.0% |
| `datasets_coresubsidyrecord` | `taxdelinquency2021` | 38.1% |
| `datasets_coresubsidyrecord` | `tenure` | 21.0% |
| `datasets_coresubsidyrecord` | `tract10id` | 99.9% |
| `datasets_coresubsidyrecord` | `yearbuilt` | 99.1% |
| `datasets_dobcomplaint` | `bbl` | 96.9% |
| `datasets_dobcomplaint` | `bin` | 100.0% |
| `datasets_dobcomplaint` | `communityboard` | 100.0% |
| `datasets_dobcomplaint` | `dispositioncode` | 97.8% |
| `datasets_dobcomplaint` | `dispositiondate` | 97.8% |
| `datasets_dobcomplaint` | `dobrundate` | 100.0% |
| `datasets_dobcomplaint` | `housenumber` | 100.0% |
| `datasets_dobcomplaint` | `housestreet` | 100.0% |
| `datasets_dobcomplaint` | `inspectiondate` | 97.8% |
| `datasets_dobcomplaint` | `specialdistrict` | 0.5% |
| `datasets_dobcomplaint` | `unit` | 100.0% |
| `datasets_dobcomplaint` | `zipcode` | 99.2% |
| `datasets_dobfiledpermit` | `applicantlicense` | 98.1% |
| `datasets_dobfiledpermit` | `applicantprofessionaltitle` | 100.0% |
| `datasets_dobfiledpermit` | `applicantsfirstname` | 100.0% |
| `datasets_dobfiledpermit` | `applicantslastname` | 100.0% |
| `datasets_dobfiledpermit` | `bbl` | 100.0% |
| `datasets_dobfiledpermit` | `bin` | 100.0% |
| `datasets_dobfiledpermit` | `borough` | 100.0% |
| `datasets_dobfiledpermit` | `foreign_key` | 100.0% |
| `datasets_dobfiledpermit` | `housenumber` | 100.0% |
| `datasets_dobfiledpermit` | `initialcost` | 100.0% |
| `datasets_dobfiledpermit` | `ownerbusinessname` | 96.1% |
| `datasets_dobfiledpermit` | `streetname` | 100.0% |
| `datasets_dobissuedpermit` | `applicantbusinessname` | 75.4% |
| `datasets_dobissuedpermit` | `applicantname` | 100.0% |
| `datasets_dobissuedpermit` | `bbl` | 100.0% |
| `datasets_dobissuedpermit` | `bin` | 100.0% |
| `datasets_dobissuedpermit` | `borough` | 100.0% |
| `datasets_dobissuedpermit` | `expirationdate` | 100.0% |
| `datasets_dobissuedpermit` | `foreign_key` | 100.0% |
| `datasets_dobissuedpermit` | `houseno` | 100.0% |
| `datasets_dobissuedpermit` | `ownerbusinessname` | 73.8% |
| `datasets_dobissuedpermit` | `ownername` | 75.4% |
| `datasets_dobissuedpermit` | `permit_status` | 75.3% |
| `datasets_dobissuedpermit` | `permit_subtype` | 42.6% |
| `datasets_dobissuedpermit` | `streetname` | 100.0% |
| `datasets_dobviolation` | `bbl` | 99.4% |
| `datasets_dobviolation` | `bin` | 99.9% |
| `datasets_dobviolation` | `block` | 99.5% |
| `datasets_dobviolation` | `boro` | 100.0% |
| `datasets_dobviolation` | `devicenumber` | 73.6% |
| `datasets_dobviolation` | `dispositioncomments` | 74.2% |
| `datasets_dobviolation` | `dispositiondate` | 76.0% |
| `datasets_dobviolation` | `ecbnumber` | 8.6% |
| `datasets_dobviolation` | `housenumber` | 100.0% |
| `datasets_dobviolation` | `lot` | 99.5% |
| `datasets_dobviolation` | `number` | 100.0% |
| `datasets_dobviolation` | `street` | 99.3% |
| `datasets_dobviolation` | `violationnumber` | 100.0% |
| `datasets_dobviolation` | `violationtypecode` | 100.0% |
| `datasets_ecbviolation` | `balancedue` | 100.0% |
| `datasets_ecbviolation` | `bbl` | 98.5% |
| `datasets_ecbviolation` | `bin` | 99.7% |
| `datasets_ecbviolation` | `block` | 98.5% |
| `datasets_ecbviolation` | `boro` | 100.0% |
| `datasets_ecbviolation` | `certificationstatus` | 94.2% |
| `datasets_ecbviolation` | `dobviolationnumber` | 88.8% |
| `datasets_ecbviolation` | `hearingdate` | 100.0% |
| `datasets_ecbviolation` | `hearingtime` | 100.0% |
| `datasets_ecbviolation` | `infractioncode1` | 100.0% |
| `datasets_ecbviolation` | `infractioncode2` | 6.0% |
| `datasets_ecbviolation` | `infractioncode3` | 0.6% |
| `datasets_ecbviolation` | `infractioncode4` | 0.2% |
| `datasets_ecbviolation` | `infractioncode5` | 0.1% |
| `datasets_ecbviolation` | `infractioncode6` | 0.1% |
| `datasets_ecbviolation` | `infractioncode7` | 0.1% |
| `datasets_ecbviolation` | `isndobbisextract` | 100.0% |
| `datasets_ecbviolation` | `lot` | 98.5% |
| `datasets_ecbviolation` | `respondentcity` | 92.2% |
| `datasets_ecbviolation` | `respondenthousenumber` | 88.7% |
| `datasets_ecbviolation` | `respondentname` | 100.0% |
| `datasets_ecbviolation` | `respondentstreet` | 92.1% |
| `datasets_ecbviolation` | `respondentzip` | 89.9% |
| `datasets_ecbviolation` | `sectionlawdescription2` | 5.9% |
| `datasets_ecbviolation` | `sectionlawdescription3` | 0.6% |
| `datasets_ecbviolation` | `sectionlawdescription4` | 0.2% |
| `datasets_ecbviolation` | `sectionlawdescription5` | 0.1% |
| `datasets_ecbviolation` | `sectionlawdescription6` | 0.1% |
| `datasets_ecbviolation` | `sectionlawdescription7` | 0.1% |
| `datasets_ecbviolation` | `serveddate` | 97.8% |
| `datasets_eviction` | `bbl` | 90.5% |
| `datasets_eviction` | `bin` | 90.5% |
| `datasets_eviction` | `borough` | 100.0% |
| `datasets_eviction` | `censustract` | 90.8% |
| `datasets_eviction` | `cleaned_address` | 6.0% |
| `datasets_eviction` | `communityboard` | 90.8% |
| `datasets_eviction` | `councildistrict` | 90.8% |
| `datasets_eviction` | `ejectment` | 100.0% |
| `datasets_eviction` | `evictionapartmentnumber` | 85.3% |
| `datasets_eviction` | `evictionlegalpossession` | 100.0% |
| `datasets_eviction` | `evictionpostcode` | 100.0% |
| `datasets_eviction` | `latitude` | 90.8% |
| `datasets_eviction` | `longitude` | 90.8% |
| `datasets_eviction` | `marshal1stname` | 100.0% |
| `datasets_eviction` | `marshallastname` | 100.0% |
| `datasets_eviction` | `nta` | 90.8% |
| `datasets_eviction` | `residentialcommercial` | 100.0% |
| `datasets_eviction` | `uniqueid` | 6.0% |
| `datasets_foreclosure` | `address` | 91.7% |
| `datasets_foreclosure` | `auction` | 10.8% |
| `datasets_foreclosure` | `bbl` | 100.0% |
| `datasets_foreclosure` | `foreign_key` | 100.0% |
| `datasets_housinglitigation` | `bbl` | 99.9% |
| `datasets_housinglitigation` | `bin` | 99.9% |
| `datasets_housinglitigation` | `block` | 100.0% |
| `datasets_housinglitigation` | `boro` | 100.0% |
| `datasets_housinglitigation` | `buildingid` | 100.0% |
| `datasets_housinglitigation` | `censustract` | 100.0% |
| `datasets_housinglitigation` | `communitydistrict` | 100.0% |
| `datasets_housinglitigation` | `councildistrict` | 100.0% |
| `datasets_housinglitigation` | `housenumber` | 100.0% |
| `datasets_housinglitigation` | `latitude` | 100.0% |
| `datasets_housinglitigation` | `longitude` | 100.0% |
| `datasets_housinglitigation` | `lot` | 100.0% |
| `datasets_housinglitigation` | `nta` | 100.0% |
| `datasets_housinglitigation` | `streetname` | 100.0% |
| `datasets_housinglitigation` | `zip` | 100.0% |
| `datasets_hpdbuildingrecord` | `bbl` | 99.9% |
| `datasets_hpdbuildingrecord` | `bin` | 96.8% |
| `datasets_hpdbuildingrecord` | `block` | 100.0% |
| `datasets_hpdbuildingrecord` | `boro` | 100.0% |
| `datasets_hpdbuildingrecord` | `boroid` | 100.0% |
| `datasets_hpdbuildingrecord` | `buildingid` | 100.0% |
| `datasets_hpdbuildingrecord` | `censustract` | 99.7% |
| `datasets_hpdbuildingrecord` | `communityboard` | 100.0% |
| `datasets_hpdbuildingrecord` | `dobbuildingclass` | 96.3% |
| `datasets_hpdbuildingrecord` | `dobbuildingclassid` | 96.3% |
| `datasets_hpdbuildingrecord` | `highhousenumber` | 100.0% |
| `datasets_hpdbuildingrecord` | `housenumber` | 100.0% |
| `datasets_hpdbuildingrecord` | `legalclassa` | 96.0% |
| `datasets_hpdbuildingrecord` | `legalclassb` | 93.6% |
| `datasets_hpdbuildingrecord` | `legalstories` | 96.1% |
| `datasets_hpdbuildingrecord` | `lifecycle` | 100.0% |
| `datasets_hpdbuildingrecord` | `lot` | 100.0% |
| `datasets_hpdbuildingrecord` | `lowhousenumber` | 100.0% |
| `datasets_hpdbuildingrecord` | `managementprogram` | 100.0% |
| `datasets_hpdbuildingrecord` | `recordstatus` | 100.0% |
| `datasets_hpdbuildingrecord` | `recordstatusid` | 100.0% |
| `datasets_hpdbuildingrecord` | `registrationid` | 100.0% |
| `datasets_hpdbuildingrecord` | `streetname` | 100.0% |
| `datasets_hpdbuildingrecord` | `zip` | 99.7% |
| `datasets_hpdcomplaint` | `bbl` | 100.0% |
| `datasets_hpdcomplaint` | `bin` | 99.8% |
| `datasets_hpdcomplaint` | `block` | 100.0% |
| `datasets_hpdcomplaint` | `borough` | 100.0% |
| `datasets_hpdcomplaint` | `buildingid` | 100.0% |
| `datasets_hpdcomplaint` | `census_tract` | 100.0% |
| `datasets_hpdcomplaint` | `communityboard` | 100.0% |
| `datasets_hpdcomplaint` | `complaintanonymousflag` | 90.9% |
| `datasets_hpdcomplaint` | `council_district` | 100.0% |
| `datasets_hpdcomplaint` | `housenumber` | 100.0% |
| `datasets_hpdcomplaint` | `latitude` | 100.0% |
| `datasets_hpdcomplaint` | `longitude` | 100.0% |
| `datasets_hpdcomplaint` | `lot` | 100.0% |
| `datasets_hpdcomplaint` | `nta` | 100.0% |
| `datasets_hpdcomplaint` | `problemduplicateflag` | 100.0% |
| `datasets_hpdcomplaint` | `problemstatusdate` | 100.0% |
| `datasets_hpdcomplaint` | `statusdate` | 100.0% |
| `datasets_hpdcomplaint` | `streetname` | 100.0% |
| `datasets_hpdcomplaint` | `uniquekey` | 86.9% |
| `datasets_hpdcomplaint` | `unittype` | 100.0% |
| `datasets_hpdcomplaint` | `zip` | 99.9% |
| `datasets_hpdcontact` | `businessapartment` | 34.5% |
| `datasets_hpdcontact` | `businesscity` | 78.5% |
| `datasets_hpdcontact` | `businesshousenumber` | 78.4% |
| `datasets_hpdcontact` | `businessstate` | 78.3% |
| `datasets_hpdcontact` | `businessstreetname` | 78.5% |
| `datasets_hpdcontact` | `businesszip` | 78.4% |
| `datasets_hpdcontact` | `contactdescription` | 99.8% |
| `datasets_hpdcontact` | `corporationname` | 26.2% |
| `datasets_hpdcontact` | `firstname` | 84.4% |
| `datasets_hpdcontact` | `lastname` | 84.3% |
| `datasets_hpdcontact` | `middleinitial` | 13.6% |
| `datasets_hpdcontact` | `registrationcontactid` | 100.0% |
| `datasets_hpdcontact` | `registrationid` | 100.0% |
| `datasets_hpdcontact` | `title` | 16.4% |
| `datasets_hpdcontact` | `type` | 100.0% |
| `datasets_hpdregistration` | `bbl` | 100.0% |
| `datasets_hpdregistration` | `bin` | 100.0% |
| `datasets_hpdregistration` | `block` | 100.0% |
| `datasets_hpdregistration` | `boro` | 100.0% |
| `datasets_hpdregistration` | `boroid` | 100.0% |
| `datasets_hpdregistration` | `buildingid` | 100.0% |
| `datasets_hpdregistration` | `communityboard` | 100.0% |
| `datasets_hpdregistration` | `highhousenumber` | 100.0% |
| `datasets_hpdregistration` | `housenumber` | 100.0% |
| `datasets_hpdregistration` | `lastregistrationdate` | 98.3% |
| `datasets_hpdregistration` | `lot` | 100.0% |
| `datasets_hpdregistration` | `lowhousenumber` | 100.0% |
| `datasets_hpdregistration` | `registrationenddate` | 100.0% |
| `datasets_hpdregistration` | `registrationid` | 100.0% |
| `datasets_hpdregistration` | `streetcode` | 100.0% |
| `datasets_hpdregistration` | `streetname` | 100.0% |
| `datasets_hpdregistration` | `zip` | 100.0% |
| `datasets_hpdviolation` | `bbl` | 99.8% |
| `datasets_hpdviolation` | `bin` | 99.8% |
| `datasets_hpdviolation` | `block` | 100.0% |
| `datasets_hpdviolation` | `boroid` | 100.0% |
| `datasets_hpdviolation` | `borough` | 100.0% |
| `datasets_hpdviolation` | `buildingid` | 100.0% |
| `datasets_hpdviolation` | `censustract` | 99.9% |
| `datasets_hpdviolation` | `certifieddate` | 35.4% |
| `datasets_hpdviolation` | `communityboard` | 99.9% |
| `datasets_hpdviolation` | `councildistrict` | 99.9% |
| `datasets_hpdviolation` | `currentstatus` | 100.0% |
| `datasets_hpdviolation` | `currentstatusdate` | 100.0% |
| `datasets_hpdviolation` | `currentstatusid` | 100.0% |
| `datasets_hpdviolation` | `highhousenumber` | 100.0% |
| `datasets_hpdviolation` | `housenumber` | 100.0% |
| `datasets_hpdviolation` | `inspectiondate` | 100.0% |
| `datasets_hpdviolation` | `latitude` | 99.9% |
| `datasets_hpdviolation` | `longitude` | 99.9% |
| `datasets_hpdviolation` | `lot` | 100.0% |
| `datasets_hpdviolation` | `lowhousenumber` | 100.0% |
| `datasets_hpdviolation` | `newcertifybydate` | 0.9% |
| `datasets_hpdviolation` | `newcorrectbydate` | 0.9% |
| `datasets_hpdviolation` | `novid` | 92.5% |
| `datasets_hpdviolation` | `novissueddate` | 92.5% |
| `datasets_hpdviolation` | `novtype` | 92.5% |
| `datasets_hpdviolation` | `nta` | 99.9% |
| `datasets_hpdviolation` | `ordernumber` | 100.0% |
| `datasets_hpdviolation` | `originalcertifybydate` | 92.5% |
| `datasets_hpdviolation` | `originalcorrectbydate` | 92.5% |
| `datasets_hpdviolation` | `postcode` | 99.9% |
| `datasets_hpdviolation` | `registrationid` | 100.0% |
| `datasets_hpdviolation` | `rentimpairing` | 100.0% |
| `datasets_hpdviolation` | `streetcode` | 100.0% |
| `datasets_hpdviolation` | `streetname` | 100.0% |
| `datasets_lispenden` | `attorney` | 30.6% |
| `datasets_lispenden` | `bbl` | 100.0% |
| `datasets_lispenden` | `bc` | 99.9% |
| `datasets_lispenden` | `disp` | 12.5% |
| `datasets_lispenden` | `entereddate` | 100.0% |
| `datasets_lispenden` | `index` | 100.0% |
| `datasets_lispenden` | `satdate` | 31.2% |
| `datasets_lispenden` | `sattype` | 61.7% |
| `datasets_lispenden` | `source` | 30.6% |
| `datasets_lispenden` | `type` | 67.2% |
| `datasets_lispenden` | `zip` | 99.9% |
| `datasets_lispendencomment` | `datecomments` | 100.0% |
| `datasets_lispendencomment` | `key` | 100.0% |
| `datasets_ocahousingcourt` | `bbl` | 57.1% |
| `datasets_ocahousingcourt` | `bct2020` | 71.4% |
| `datasets_ocahousingcourt` | `bctcb2020` | 71.4% |
| `datasets_ocahousingcourt` | `boro` | 74.2% |
| `datasets_ocahousingcourt` | `cb2010` | 71.4% |
| `datasets_ocahousingcourt` | `cd` | 71.8% |
| `datasets_ocahousingcourt` | `city` | 100.0% |
| `datasets_ocahousingcourt` | `council` | 71.8% |
| `datasets_ocahousingcourt` | `ct` | 71.4% |
| `datasets_ocahousingcourt` | `ct2010` | 71.4% |
| `datasets_ocahousingcourt` | `firstpaper` | 100.0% |
| `datasets_ocahousingcourt` | `grc` | 98.3% |
| `datasets_ocahousingcourt` | `grc2` | 98.3% |
| `datasets_ocahousingcourt` | `msg` | 29.3% |
| `datasets_ocahousingcourt` | `msg2` | 36.4% |
| `datasets_ocahousingcourt` | `postalcode` | 100.0% |
| `datasets_ocahousingcourt` | `primaryclaimtotal` | 100.0% |
| `datasets_ocahousingcourt` | `specialtydesignationtypes` | 55.3% |
| `datasets_ocahousingcourt` | `state` | 100.0% |
| `datasets_ocahousingcourt` | `unitsres` | 71.4% |
| `datasets_property` | `appbbl` | 12.0% |
| `datasets_property` | `appdate` | 11.6% |
| `datasets_property` | `areasource` | 99.9% |
| `datasets_property` | `assessland` | 99.9% |
| `datasets_property` | `assesstot` | 99.9% |
| `datasets_property` | `basempdate` | 0.3% |
| `datasets_property` | `bct2020` | 98.5% |
| `datasets_property` | `bctcb2020` | 98.5% |
| `datasets_property` | `bldgarea` | 99.9% |
| `datasets_property` | `bldgclass` | 99.9% |
| `datasets_property` | `bldgdepth` | 99.3% |
| `datasets_property` | `bldgfront` | 99.3% |
| `datasets_property` | `block` | 100.0% |
| `datasets_property` | `borocode` | 100.0% |
| `datasets_property` | `bsmtcode` | 99.9% |
| `datasets_property` | `cb2010` | 99.3% |
| `datasets_property` | `censustract2010` | 98.4% |
| `datasets_property` | `comarea` | 94.1% |
| `datasets_property` | `condono` | 1.7% |
| `datasets_property` | `councildistrict` | 98.3% |
| `datasets_property` | `ct2010` | 99.1% |
| `datasets_property` | `dcasdate` | 0.3% |
| `datasets_property` | `dcpedited` | 4.8% |
| `datasets_property` | `easements` | 99.9% |
| `datasets_property` | `edesigdate` | 0.3% |
| `datasets_property` | `edesignum` | 1.3% |
| `datasets_property` | `exemptland` | 98.7% |
| `datasets_property` | `exempttot` | 99.9% |
| `datasets_property` | `ext` | 91.3% |
| `datasets_property` | `factryarea` | 94.1% |
| `datasets_property` | `firecomp` | 99.2% |
| `datasets_property` | `firm07flag` | 4.0% |
| `datasets_property` | `garagearea` | 94.1% |
| `datasets_property` | `geom` | 0.3% |
| `datasets_property` | `healtharea` | 99.2% |
| `datasets_property` | `healthcenterdistrict` | 99.2% |
| `datasets_property` | `histdist` | 3.6% |
| `datasets_property` | `irrlotcode` | 99.9% |
| `datasets_property` | `landmark` | 0.2% |
| `datasets_property` | `landmkdate` | 0.3% |
| `datasets_property` | `landuse` | 99.6% |
| `datasets_property` | `lat` | 98.7% |
| `datasets_property` | `lng` | 98.7% |
| `datasets_property` | `lot` | 100.0% |
| `datasets_property` | `lotarea` | 99.3% |
| `datasets_property` | `lotdepth` | 99.3% |
| `datasets_property` | `lotfront` | 99.3% |
| `datasets_property` | `lottype` | 99.9% |
| `datasets_property` | `ltdheight` | 0.4% |
| `datasets_property` | `numbldgs` | 99.3% |
| `datasets_property` | `numfloors` | 94.4% |
| `datasets_property` | `officearea` | 94.1% |
| `datasets_property` | `original_address` | 99.6% |
| `datasets_property` | `otherarea` | 94.1% |
| `datasets_property` | `ownertype` | 4.7% |
| `datasets_property` | `pfirm15flag` | 7.6% |
| `datasets_property` | `plutomapid` | 100.0% |
| `datasets_property` | `policeprct` | 99.2% |
| `datasets_property` | `proxcode` | 99.9% |
| `datasets_property` | `resarea` | 94.1% |
| `datasets_property` | `retailarea` | 94.1% |
| `datasets_property` | `rpaddate` | 0.3% |
| `datasets_property` | `sanborn` | 99.0% |
| `datasets_property` | `sanitboro` | 99.2% |
| `datasets_property` | `sanitdistrict` | 99.2% |
| `datasets_property` | `sanitsub` | 99.2% |
| `datasets_property` | `schooldist` | 99.2% |
| `datasets_property` | `splitzone` | 98.8% |
| `datasets_property` | `strgearea` | 94.1% |
| `datasets_property` | `taxmap` | 99.0% |
| `datasets_property` | `tract2010` | 99.4% |
| `datasets_property` | `version` | 100.0% |
| `datasets_property` | `xcoord` | 99.1% |
| `datasets_property` | `ycoord` | 99.1% |
| `datasets_property` | `yearalter1` | 99.9% |
| `datasets_property` | `yearalter2` | 99.9% |
| `datasets_property` | `zmcode` | 1.8% |
| `datasets_property` | `zonemap` | 98.8% |
| `datasets_property` | `zoningdate` | 0.3% |
| `datasets_propertyannotation` | `acrisrealmasters_last30` | 100.0% |
| `datasets_propertyannotation` | `acrisrealmasters_last3years` | 100.0% |
| `datasets_propertyannotation` | `acrisrealmasters_lastupdated` | 100.0% |
| `datasets_propertyannotation` | `acrisrealmasters_lastyear` | 100.0% |
| `datasets_propertyannotation` | `aepdischargedate` | 0.3% |
| `datasets_propertyannotation` | `aepstartdate` | 0.4% |
| `datasets_propertyannotation` | `aepstatus` | 100.0% |
| `datasets_propertyannotation` | `bbl` | 100.0% |
| `datasets_propertyannotation` | `conhrecord` | 100.0% |
| `datasets_propertyannotation` | `dobcomplaints_last30` | 100.0% |
| `datasets_propertyannotation` | `dobcomplaints_last3years` | 100.0% |
| `datasets_propertyannotation` | `dobcomplaints_lastupdated` | 100.0% |
| `datasets_propertyannotation` | `dobcomplaints_lastyear` | 100.0% |
| `datasets_propertyannotation` | `dobfiledpermits_last30` | 100.0% |
| `datasets_propertyannotation` | `dobfiledpermits_last3years` | 100.0% |
| `datasets_propertyannotation` | `dobfiledpermits_lastupdated` | 100.0% |
| `datasets_propertyannotation` | `dobfiledpermits_lastyear` | 100.0% |
| `datasets_propertyannotation` | `dobissuedpermits_last30` | 100.0% |
| `datasets_propertyannotation` | `dobissuedpermits_last3years` | 100.0% |
| `datasets_propertyannotation` | `dobissuedpermits_lastupdated` | 100.0% |
| `datasets_propertyannotation` | `dobissuedpermits_lastyear` | 100.0% |
| `datasets_propertyannotation` | `dobviolations_last30` | 100.0% |
| `datasets_propertyannotation` | `dobviolations_last3years` | 100.0% |
| `datasets_propertyannotation` | `dobviolations_lastupdated` | 100.0% |
| `datasets_propertyannotation` | `dobviolations_lastyear` | 100.0% |
| `datasets_propertyannotation` | `ecbviolations_last30` | 100.0% |
| `datasets_propertyannotation` | `ecbviolations_last3years` | 100.0% |
| `datasets_propertyannotation` | `ecbviolations_lastupdated` | 100.0% |
| `datasets_propertyannotation` | `ecbviolations_lastyear` | 100.0% |
| `datasets_propertyannotation` | `evictions_last30` | 100.0% |
| `datasets_propertyannotation` | `evictions_last3years` | 100.0% |
| `datasets_propertyannotation` | `evictions_lastupdated` | 100.0% |
| `datasets_propertyannotation` | `evictions_lastyear` | 100.0% |
| `datasets_propertyannotation` | `foreclosures_last30` | 100.0% |
| `datasets_propertyannotation` | `foreclosures_last3years` | 100.0% |
| `datasets_propertyannotation` | `foreclosures_lastupdated` | 100.0% |
| `datasets_propertyannotation` | `foreclosures_lastyear` | 100.0% |
| `datasets_propertyannotation` | `housinglitigations_last30` | 100.0% |
| `datasets_propertyannotation` | `housinglitigations_last3years` | 100.0% |
| `datasets_propertyannotation` | `housinglitigations_lastupdated` | 100.0% |
| `datasets_propertyannotation` | `housinglitigations_lastyear` | 100.0% |
| `datasets_propertyannotation` | `hpdcomplaints_last30` | 100.0% |
| `datasets_propertyannotation` | `hpdcomplaints_last3years` | 100.0% |
| `datasets_propertyannotation` | `hpdcomplaints_lastupdated` | 100.0% |
| `datasets_propertyannotation` | `hpdcomplaints_lastyear` | 100.0% |
| `datasets_propertyannotation` | `hpdviolations_last30` | 100.0% |
| `datasets_propertyannotation` | `hpdviolations_last3years` | 100.0% |
| `datasets_propertyannotation` | `hpdviolations_lastupdated` | 100.0% |
| `datasets_propertyannotation` | `hpdviolations_lastyear` | 100.0% |
| `datasets_propertyannotation` | `latestsaledate` | 81.4% |
| `datasets_propertyannotation` | `latestsaleprice` | 81.4% |
| `datasets_propertyannotation` | `legalclassa` | 38.5% |
| `datasets_propertyannotation` | `legalclassb` | 37.8% |
| `datasets_propertyannotation` | `managementprogram` | 100.0% |
| `datasets_propertyannotation` | `nycha` | 100.0% |
| `datasets_propertyannotation` | `ocahousingcourts_last30` | 100.0% |
| `datasets_propertyannotation` | `ocahousingcourts_last3years` | 100.0% |
| `datasets_propertyannotation` | `ocahousingcourts_lastupdated` | 100.0% |
| `datasets_propertyannotation` | `ocahousingcourts_lastyear` | 100.0% |
| `datasets_propertyannotation` | `subsidy421a` | 100.0% |
| `datasets_propertyannotation` | `subsidyj51` | 100.0% |
| `datasets_propertyannotation` | `subsidyprograms` | 2.4% |
| `datasets_propertyannotation` | `taxlien` | 100.0% |
| `datasets_propertyannotation` | `unitsrentstabilized` | 100.0% |
| `datasets_psforeclosure` | `address` | 100.0% |
| `datasets_psforeclosure` | `auctiontime` | 100.0% |
| `datasets_psforeclosure` | `bbl` | 100.0% |
| `datasets_psforeclosure` | `buildingclass` | 99.7% |
| `datasets_psforeclosure` | `hasphoto` | 89.6% |
| `datasets_psforeclosure` | `judgment` | 92.8% |
| `datasets_psforeclosure` | `legalprocess` | 49.9% |
| `datasets_psforeclosure` | `neighborhood` | 99.8% |
| `datasets_psforeclosure` | `plaintiffsattorney` | 99.4% |
| `datasets_psforeclosure` | `referee` | 93.0% |
| `datasets_psforeclosure` | `schooldistrict` | 99.5% |
| `datasets_psforeclosure` | `unitnumber` | 16.4% |
| `datasets_psforeclosure` | `zipcode` | 99.4% |
| `datasets_pspreforeclosure` | `address` | 100.0% |
| `datasets_pspreforeclosure` | `bbl` | 100.0% |
| `datasets_pspreforeclosure` | `buildingclass` | 78.9% |
| `datasets_pspreforeclosure` | `creditor` | 100.0% |
| `datasets_pspreforeclosure` | `dateadded` | 100.0% |
| `datasets_pspreforeclosure` | `debtor` | 100.0% |
| `datasets_pspreforeclosure` | `debtoraddress` | 16.7% |
| `datasets_pspreforeclosure` | `documenttype` | 95.5% |
| `datasets_pspreforeclosure` | `effectivedate` | 87.0% |
| `datasets_pspreforeclosure` | `hasphoto` | 89.8% |
| `datasets_pspreforeclosure` | `indexno` | 100.0% |
| `datasets_pspreforeclosure` | `key` | 100.0% |
| `datasets_pspreforeclosure` | `lientype` | 66.9% |
| `datasets_pspreforeclosure` | `mortgagedate` | 52.9% |
| `datasets_pspreforeclosure` | `neighborhood` | 97.2% |
| `datasets_pspreforeclosure` | `schooldistrict` | 98.1% |
| `datasets_pspreforeclosure` | `taxvalue` | 98.4% |
| `datasets_pspreforeclosure` | `zipcode` | 99.2% |
| `datasets_publichousingrecord` | `address` | 100.0% |
| `datasets_publichousingrecord` | `bbl` | 100.0% |
| `datasets_publichousingrecord` | `block` | 100.0% |
| `datasets_publichousingrecord` | `borough` | 100.0% |
| `datasets_publichousingrecord` | `cd` | 100.0% |
| `datasets_publichousingrecord` | `development` | 100.0% |
| `datasets_publichousingrecord` | `facility` | 47.0% |
| `datasets_publichousingrecord` | `lot` | 100.0% |
| `datasets_publichousingrecord` | `managedby` | 100.0% |
| `datasets_publichousingrecord` | `zipcode` | 100.0% |
| `datasets_rentstabilizationrecord` | `abat2009` | 43.0% |
| `datasets_rentstabilizationrecord` | `abat2010` | 43.8% |
| `datasets_rentstabilizationrecord` | `abat2011` | 44.5% |
| `datasets_rentstabilizationrecord` | `abat2012` | 44.7% |
| `datasets_rentstabilizationrecord` | `abat2013` | 45.8% |
| `datasets_rentstabilizationrecord` | `abat2014` | 42.2% |
| `datasets_rentstabilizationrecord` | `abat2015` | 23.7% |
| `datasets_rentstabilizationrecord` | `abat2016` | 21.6% |
| `datasets_rentstabilizationrecord` | `abat2017` | 43.2% |
| `datasets_rentstabilizationrecord` | `address` | 88.4% |
| `datasets_rentstabilizationrecord` | `borough` | 88.4% |
| `datasets_rentstabilizationrecord` | `cb2010` | 88.3% |
| `datasets_rentstabilizationrecord` | `cd` | 88.4% |
| `datasets_rentstabilizationrecord` | `condono` | 88.4% |
| `datasets_rentstabilizationrecord` | `council` | 88.4% |
| `datasets_rentstabilizationrecord` | `ct2010` | 88.4% |
| `datasets_rentstabilizationrecord` | `dhcr2009` | 70.0% |
| `datasets_rentstabilizationrecord` | `dhcr2011` | 69.2% |
| `datasets_rentstabilizationrecord` | `dhcr2012` | 72.6% |
| `datasets_rentstabilizationrecord` | `dhcr2013` | 73.0% |
| `datasets_rentstabilizationrecord` | `est2007` | 89.1% |
| `datasets_rentstabilizationrecord` | `est2008` | 89.1% |
| `datasets_rentstabilizationrecord` | `est2009` | 89.1% |
| `datasets_rentstabilizationrecord` | `est2010` | 89.1% |
| `datasets_rentstabilizationrecord` | `est2011` | 89.1% |
| `datasets_rentstabilizationrecord` | `est2012` | 89.1% |
| `datasets_rentstabilizationrecord` | `est2013` | 89.1% |
| `datasets_rentstabilizationrecord` | `est2014` | 89.1% |
| `datasets_rentstabilizationrecord` | `est2015` | 89.1% |
| `datasets_rentstabilizationrecord` | `est2016` | 89.1% |
| `datasets_rentstabilizationrecord` | `est2017` | 89.1% |
| `datasets_rentstabilizationrecord` | `lat` | 87.9% |
| `datasets_rentstabilizationrecord` | `latestuctotals` | 73.3% |
| `datasets_rentstabilizationrecord` | `lon` | 87.9% |
| `datasets_rentstabilizationrecord` | `numbldgs` | 88.4% |
| `datasets_rentstabilizationrecord` | `numfloors` | 88.4% |
| `datasets_rentstabilizationrecord` | `ownername` | 87.4% |
| `datasets_rentstabilizationrecord` | `pdfsoa2018` | 81.8% |
| `datasets_rentstabilizationrecord` | `pdfsoa2019` | 96.3% |
| `datasets_rentstabilizationrecord` | `uc2007` | 78.7% |
| `datasets_rentstabilizationrecord` | `uc2008` | 78.7% |
| `datasets_rentstabilizationrecord` | `uc2009` | 73.7% |
| `datasets_rentstabilizationrecord` | `uc2010` | 73.0% |
| `datasets_rentstabilizationrecord` | `uc2011` | 74.7% |
| `datasets_rentstabilizationrecord` | `uc2012` | 76.2% |
| `datasets_rentstabilizationrecord` | `uc2013` | 76.4% |
| `datasets_rentstabilizationrecord` | `uc2014` | 74.5% |
| `datasets_rentstabilizationrecord` | `uc2015` | 73.4% |
| `datasets_rentstabilizationrecord` | `uc2016` | 72.9% |
| `datasets_rentstabilizationrecord` | `uc2017` | 72.3% |
| `datasets_rentstabilizationrecord` | `uc2018` | 77.1% |
| `datasets_rentstabilizationrecord` | `uc2019` | 72.5% |
| `datasets_rentstabilizationrecord` | `uc2020` | 56.4% |
| `datasets_rentstabilizationrecord` | `uc2021` | 56.3% |
| `datasets_rentstabilizationrecord` | `uc2022` | 54.2% |
| `datasets_rentstabilizationrecord` | `uc2023` | 88.7% |
| `datasets_rentstabilizationrecord` | `ucbbl` | 100.0% |
| `datasets_rentstabilizationrecord` | `unitsres` | 88.4% |
| `datasets_rentstabilizationrecord` | `unitstotal` | 88.4% |
| `datasets_rentstabilizationrecord` | `yearbuilt` | 88.4% |
| `datasets_rentstabilizationrecord` | `zipcode` | 88.4% |
| `datasets_subsidyj51` | `address` | 100.0% |
| `datasets_subsidyj51` | `bbl` | 100.0% |
| `datasets_subsidyj51` | `block` | 100.0% |
| `datasets_subsidyj51` | `borough` | 100.0% |
| `datasets_subsidyj51` | `buildingclassatpresent` | 100.0% |
| `datasets_subsidyj51` | `buildingclasscategory` | 100.0% |
| `datasets_subsidyj51` | `commercialunits` | 100.0% |
| `datasets_subsidyj51` | `grosssquarefeet` | 100.0% |
| `datasets_subsidyj51` | `landsquarefeet` | 100.0% |
| `datasets_subsidyj51` | `lot` | 100.0% |
| `datasets_subsidyj51` | `neighborhood` | 100.0% |
| `datasets_subsidyj51` | `residentialunits` | 100.0% |
| `datasets_subsidyj51` | `taxclassatpresent` | 100.0% |
| `datasets_subsidyj51` | `totalunits` | 100.0% |
| `datasets_subsidyj51` | `yearbuilt` | 100.0% |
| `datasets_subsidyj51` | `zipcode` | 100.0% |
| `datasets_taxlien` | `bbl` | 100.0% |
| `datasets_taxlien` | `block` | 100.0% |
| `datasets_taxlien` | `borough` | 100.0% |
| `datasets_taxlien` | `buildingclass` | 100.0% |
| `datasets_taxlien` | `communityboard` | 98.6% |
| `datasets_taxlien` | `councildistrict` | 98.9% |
| `datasets_taxlien` | `cycle` | 100.0% |
| `datasets_taxlien` | `housenumber` | 89.6% |
| `datasets_taxlien` | `lot` | 100.0% |
| `datasets_taxlien` | `month` | 100.0% |
| `datasets_taxlien` | `streetname` | 99.9% |
| `datasets_taxlien` | `taxclasscode` | 100.0% |
| `datasets_taxlien` | `waterdebtonly` | 100.0% |
| `datasets_taxlien` | `year` | 100.0% |
| `datasets_taxlien` | `zipcode` | 92.2% |

---

## Per-Table Field Audit

### `datasets_acrisreallegal`

**Row count:** 22,373,669

#### Partially Populated (3 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `streetname` | 16,062,340 | 6,311,329 | 71.8% | Not used by frontend |
| `streetnumber` | 15,951,660 | 6,422,009 | 71.3% | Not used by frontend |
| `unit` | 5,017,217 | 17,356,452 | 22.4% | Not used by frontend |

#### Always Populated (13 fields)

| Field | Frontend Usage |
|-------|----------------|
| `airrights` | Not used by frontend |
| `bbl` | Not used by frontend |
| `block` | Not used by frontend |
| `borough` | Not used by frontend |
| `documentid` | Not used by frontend |
| `easement` | Not used by frontend |
| `goodthroughdate` | Not used by frontend |
| `key` | Not used by frontend |
| `lot` | Not used by frontend |
| `partiallot` | Not used by frontend |
| `propertytype` | Not used by frontend |
| `recordtype` | Not used by frontend |
| `subterraneanrights` | Not used by frontend |

---

### `datasets_acrisrealmaster`

**Row count:** 16,921,049

#### Partially Populated (2 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `crfn` | 9,108,923 | 7,812,126 | 53.8% | Not used by frontend |
| `docdate` | 12,106,736 | 4,814,313 | 71.5% | Table column (Document Date) |

#### Always Populated (12 fields)

| Field | Frontend Usage |
|-------|----------------|
| `borough` | Not used by frontend |
| `docamount` | Table column (Amount), dollarFormatter |
| `doctype` | Table column (Document Type), filter buttons (Deeds/Mortgages) |
| `documentid` | Table column (Document ID), links to ACRIS |
| `goodthroughdate` | Not used by frontend |
| `modifieddate` | Not used by frontend |
| `pcttransferred` | Not used by frontend |
| `recordedfiled` | Table column (Filing Date) |
| `recordtype` | Not used by frontend |
| `reelnbr` | Not used by frontend |
| `reelpage` | Not used by frontend |
| `reelyear` | Not used by frontend |

---

### `datasets_acrisrealparty`

**Row count:** 45,271,670

#### Partially Populated (6 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `address1` | 29,373,439 | 15,898,231 | 64.9% | Table column (Address 1), text filter |
| `address2` | 3,904,277 | 41,367,393 | 8.6% | Table column (Address 2), text filter |
| `city` | 29,368,207 | 15,903,463 | 64.9% | Table column (City), text filter |
| `country` | 32,981,815 | 12,289,855 | 72.9% | Table column (Country), text filter |
| `state` | 29,348,421 | 15,923,249 | 64.8% | Table column (State), text filter |
| `zip` | 28,900,141 | 16,371,529 | 63.8% | Table column (Zip), text filter |

#### Always Populated (6 fields)

| Field | Frontend Usage |
|-------|----------------|
| `documentid` | Table column (Document ID) |
| `goodthroughdate` | Not used by frontend |
| `key` | Hidden keyField |
| `name` | Table column (Name), expandable, text filter |
| `partytype` | Table column (Party Type), text filter |
| `recordtype` | Not used by frontend |

---

### `datasets_addressrecord`

**Row count:** 1,407,419

#### Partially Populated (4 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `bin` | 540,673 | 866,746 | 38.4% | Infrastructure/lookup - not directly displayed |
| `number` | 1,384,360 | 23,059 | 98.4% | Infrastructure/lookup - not directly displayed |
| `pad_address` | 542,082 | 865,337 | 38.5% | Infrastructure/lookup - not directly displayed |
| `zipcode` | 1,404,307 | 3,112 | 99.8% | Infrastructure/lookup - not directly displayed |

#### Always Populated (6 fields)

| Field | Frontend Usage |
|-------|----------------|
| `address` | Infrastructure/lookup - not directly displayed |
| `bbl` | Infrastructure/lookup - not directly displayed |
| `borough` | Infrastructure/lookup - not directly displayed |
| `created` | Infrastructure/lookup - not directly displayed |
| `key` | Infrastructure/lookup - not directly displayed |
| `street` | Infrastructure/lookup - not directly displayed |

---

### `datasets_aepbuilding`

**Row count:** 3,706

#### Partially Populated (10 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `bbl` | 3,697 | 9 | 99.8% | Not used by frontend |
| `bin` | 3,697 | 9 | 99.8% | Not used by frontend |
| `censustract` | 3,701 | 5 | 99.9% | Not used by frontend |
| `communityboard` | 3,701 | 5 | 99.9% | Not used by frontend |
| `councildistrict` | 3,701 | 5 | 99.9% | Not used by frontend |
| `dischargedate` | 2,813 | 893 | 75.9% | Not used by frontend |
| `latitude` | 3,701 | 5 | 99.9% | Not used by frontend |
| `longitude` | 3,701 | 5 | 99.9% | Not used by frontend |
| `nta` | 3,701 | 5 | 99.9% | Not used by frontend |
| `postcode` | 3,701 | 5 | 99.9% | Not used by frontend |

#### Always Populated (9 fields)

| Field | Frontend Usage |
|-------|----------------|
| `aepround` | Not used by frontend |
| `aepstartdate` | Not used by frontend |
| `borough` | Not used by frontend |
| `buildingid` | Not used by frontend |
| `currentstatus` | Not used by frontend |
| `number` | Not used by frontend |
| `ofbcviolationsatstart` | Not used by frontend |
| `street` | Not used by frontend |
| `totalunits` | Not used by frontend |

---

### `datasets_building`

**Row count:** 1,084,857

#### Always NULL (2 fields)

| Field | Frontend Usage |
|-------|----------------|
| `dapsflag` | Infrastructure/lookup - not directly displayed |
| `naubflag` | Infrastructure/lookup - not directly displayed |

#### Partially Populated (5 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `addrtype` | 573 | 1,084,284 | 0.1% | Infrastructure/lookup - not directly displayed |
| `hcontpar` | 4,045 | 1,080,812 | 0.4% | Infrastructure/lookup - not directly displayed |
| `lcontpar` | 4,041 | 1,080,816 | 0.4% | Infrastructure/lookup - not directly displayed |
| `physicalid` | 1,062,814 | 22,043 | 98.0% | Infrastructure/lookup - not directly displayed |
| `realb7sc` | 583 | 1,084,274 | 0.1% | Infrastructure/lookup - not directly displayed |

#### Always Populated (21 fields)

| Field | Frontend Usage |
|-------|----------------|
| `b10sc` | Infrastructure/lookup - not directly displayed |
| `bbl` | Infrastructure/lookup - not directly displayed |
| `bin` | Infrastructure/lookup - not directly displayed |
| `block` | Infrastructure/lookup - not directly displayed |
| `boro` | Infrastructure/lookup - not directly displayed |
| `hhnd` | Infrastructure/lookup - not directly displayed |
| `hhns` | Infrastructure/lookup - not directly displayed |
| `hsos` | Infrastructure/lookup - not directly displayed |
| `lhnd` | Infrastructure/lookup - not directly displayed |
| `lhns` | Infrastructure/lookup - not directly displayed |
| `lot` | Infrastructure/lookup - not directly displayed |
| `lsos` | Infrastructure/lookup - not directly displayed |
| `pad_addresses` | Infrastructure/lookup - not directly displayed |
| `parity` | Infrastructure/lookup - not directly displayed |
| `sc5` | Infrastructure/lookup - not directly displayed |
| `scboro` | Infrastructure/lookup - not directly displayed |
| `sclgc` | Infrastructure/lookup - not directly displayed |
| `segid` | Infrastructure/lookup - not directly displayed |
| `stname` | Infrastructure/lookup - not directly displayed |
| `validlgcs` | Infrastructure/lookup - not directly displayed |
| `zipcode` | Infrastructure/lookup - not directly displayed |

---

### `datasets_community`

**Row count:** 71

#### Always Populated (1 fields)

| Field | Frontend Usage |
|-------|----------------|
| `data` | Infrastructure/lookup - not directly displayed |

---

### `datasets_conhrecord`

**Row count:** 1,519

#### Always NULL (3 fields)

| Field | Frontend Usage |
|-------|----------------|
| `aeporder` | Not used by frontend |
| `censustract` | Not used by frontend |
| `ntaneighborhoodtabulationarea` | Not used by frontend |

#### Always Populated (22 fields)

| Field | Frontend Usage |
|-------|----------------|
| `bbl` | Not used by frontend |
| `bin` | Not used by frontend |
| `block` | Not used by frontend |
| `borocode` | Not used by frontend |
| `borough` | Not used by frontend |
| `bqi` | Not used by frontend |
| `buildingid` | Not used by frontend |
| `censustract2020` | Not used by frontend |
| `communityboard` | Not used by frontend |
| `councildistrict` | Not used by frontend |
| `dateadded` | Not used by frontend |
| `discharged7a` | Not used by frontend |
| `dischargedaep` | Not used by frontend |
| `dobvacateorder` | Not used by frontend |
| `harassmentfinding` | Not used by frontend |
| `hpdvacateorder` | Not used by frontend |
| `latitude` | Not used by frontend |
| `longitude` | Not used by frontend |
| `lot` | Not used by frontend |
| `neighborhoodtabulationareanta2020` | Not used by frontend |
| `postcode` | Not used by frontend |
| `streetaddress` | Not used by frontend |

---

### `datasets_coresubsidyrecord`

**Row count:** 21,133

#### Always NULL (6 fields)

| Field | Frontend Usage |
|-------|----------------|
| `serviolation2017` | Not used by frontend |
| `serviolation2018` | Not used by frontend |
| `serviolation2019` | Not used by frontend |
| `taxdelinquency2016` | Not used by frontend |
| `taxdelinquency2018` | Not used by frontend |
| `taxdelinquency2019` | Not used by frontend |

#### Partially Populated (21 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `agencysuppliedid1` | 11,227 | 9,906 | 53.1% | Not used by frontend |
| `agencysuppliedid2` | 3,899 | 17,234 | 18.4% | Not used by frontend |
| `buildings` | 21,072 | 61 | 99.7% | Not used by frontend |
| `cdname` | 21,118 | 15 | 99.9% | Not used by frontend |
| `enddate` | 14,023 | 7,110 | 66.4% | Not used by frontend |
| `latitude` | 20,345 | 788 | 96.3% | Not used by frontend |
| `longitude` | 20,345 | 788 | 96.3% | Not used by frontend |
| `preservation` | 13,330 | 7,803 | 63.1% | Not used by frontend |
| `projectname` | 10,869 | 10,264 | 51.4% | Not used by frontend |
| `pumaid` | 21,119 | 14 | 99.9% | Not used by frontend |
| `pumaname` | 21,119 | 14 | 99.9% | Not used by frontend |
| `reacdate` | 23 | 21,110 | 0.1% | Not used by frontend |
| `reacscore` | 785 | 20,348 | 3.7% | Not used by frontend |
| `resunits` | 20,850 | 283 | 98.7% | Not used by frontend |
| `serviolation2021` | 8,663 | 12,470 | 41.0% | Not used by frontend |
| `standardaddress` | 21,118 | 15 | 99.9% | Not used by frontend |
| `startdate` | 20,711 | 422 | 98.0% | Not used by frontend |
| `taxdelinquency2021` | 8,047 | 13,086 | 38.1% | Not used by frontend |
| `tenure` | 4,435 | 16,698 | 21.0% | Not used by frontend |
| `tract10id` | 21,119 | 14 | 99.9% | Not used by frontend |
| `yearbuilt` | 20,947 | 186 | 99.1% | Not used by frontend |

#### Always Populated (12 fields)

| Field | Frontend Usage |
|-------|----------------|
| `agencyname` | Not used by frontend |
| `assessedvalue` | Not used by frontend |
| `bbl` | Not used by frontend |
| `boroname` | Not used by frontend |
| `ccdid` | Not used by frontend |
| `ccdname` | Not used by frontend |
| `cdid` | Not used by frontend |
| `dataoutputdate` | Not used by frontend |
| `fcsubsidyid` | Not used by frontend |
| `ownername` | Not used by frontend |
| `programname` | Not used by frontend |
| `regulatorytool` | Not used by frontend |

---

### `datasets_council`

**Row count:** 51

#### Always Populated (1 fields)

| Field | Frontend Usage |
|-------|----------------|
| `data` | Infrastructure/lookup - not directly displayed |

---

### `datasets_dobcomplaint`

**Row count:** 3,086,811

#### Partially Populated (6 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `bbl` | 2,991,898 | 94,913 | 96.9% | Not used by frontend |
| `dispositioncode` | 3,017,735 | 69,076 | 97.8% | Not used by frontend |
| `dispositiondate` | 3,017,734 | 69,077 | 97.8% | Not used by frontend |
| `inspectiondate` | 3,017,734 | 69,077 | 97.8% | Not used by frontend |
| `specialdistrict` | 16,733 | 3,070,078 | 0.5% | Not used by frontend |
| `zipcode` | 3,063,525 | 23,286 | 99.2% | Not used by frontend |

#### Always Populated (10 fields)

| Field | Frontend Usage |
|-------|----------------|
| `bin` | Not used by frontend |
| `communityboard` | Not used by frontend |
| `complaintcategory` | Table column (Category & Priority) |
| `complaintnumber` | Table column (Complaint #), link to BIS, keyField |
| `dateentered` | Table column (Date Entered), dateFormatter |
| `dobrundate` | Not used by frontend |
| `housenumber` | Not used by frontend |
| `housestreet` | Not used by frontend |
| `status` | Table column (Status), filter buttons (Active/Closed) |
| `unit` | Not used by frontend |

---

### `datasets_dobfiledpermit`

**Row count:** 2,508,790

#### Partially Populated (4 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `applicantlicense` | 2,460,168 | 48,622 | 98.1% | Not used by frontend |
| `datefiled` | 2,505,984 | 2,806 | 99.9% | Table column (Date Filed) |
| `jobdescription` | 2,287,350 | 221,440 | 91.2% | Table column (Description), expandable |
| `ownerbusinessname` | 2,410,227 | 98,563 | 96.1% | Not used by frontend |

#### Always Populated (16 fields)

| Field | Frontend Usage |
|-------|----------------|
| `applicantprofessionaltitle` | Not used by frontend |
| `applicantsfirstname` | Not used by frontend |
| `applicantslastname` | Not used by frontend |
| `bbl` | Not used by frontend |
| `bin` | Not used by frontend |
| `borough` | Not used by frontend |
| `foreign_key` | Not used by frontend |
| `housenumber` | Not used by frontend |
| `initialcost` | Not used by frontend |
| `job_type` | Table column (Job Type), filter dropdown |
| `jobfilingnumber` | Table column (Job Filing #), link |
| `jobstatus` | Table column (Status) |
| `jobtype` | Hidden, used in filter logic |
| `key` | Hidden keyField |
| `streetname` | Not used by frontend |
| `type` | Table column (Source) |

---

### `datasets_dobissuedpermit`

**Row count:** 2,183,879

#### Partially Populated (9 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `applicantbusinessname` | 1,647,684 | 536,195 | 75.4% | Not used by frontend |
| `filing_reason` | 536,172 | 1,647,707 | 24.6% | Used in filing_status formatter |
| `filing_status` | 1,647,707 | 536,172 | 75.4% | Table column (Filing Status) |
| `ownerbusinessname` | 1,612,784 | 571,095 | 73.8% | Not used by frontend |
| `ownername` | 1,647,707 | 536,172 | 75.4% | Not used by frontend |
| `permit_status` | 1,643,488 | 540,391 | 75.3% | Not used by frontend |
| `permit_subtype` | 930,134 | 1,253,745 | 42.6% | Not used by frontend |
| `permit_type` | 1,647,706 | 536,173 | 75.4% | Table column (Permit Type) |
| `worktype` | 1,955,511 | 228,368 | 89.5% | Table column (Work Type) |

#### Always Populated (14 fields)

| Field | Frontend Usage |
|-------|----------------|
| `applicantname` | Not used by frontend |
| `bbl` | Not used by frontend |
| `bin` | Not used by frontend |
| `borough` | Not used by frontend |
| `expirationdate` | Not used by frontend |
| `foreign_key` | Not used by frontend |
| `houseno` | Not used by frontend |
| `issuedate` | Table column (Date Issued) |
| `jobdescription` | Table column (Description), expandable |
| `jobfilingnumber` | Hidden, used for sorting/linking |
| `key` | Hidden keyField |
| `streetname` | Not used by frontend |
| `type` | Table column (Source) |
| `workpermit` | Table column (Work Permit) |

---

### `datasets_doblegacyfiledpermit`

**Row count:** 2,714,575

> Note: Merges into DOB_FILED_PERMIT joined table for frontend display

#### Always NULL (7 fields)

| Field | Frontend Usage |
|-------|----------------|
| `city` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `horizontalenlrgmt` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `ownershousenumber` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `ownershousestreetname` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `state` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `verticalenlrgmt` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `zip` | Merges into DOB_FILED_PERMIT joined table for frontend display |

#### Partially Populated (54 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `adultestab` | 2,413,063 | 301,512 | 88.9% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `applicantlicense` | 2,637,992 | 76,583 | 97.2% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `approved` | 2,216,206 | 498,369 | 81.6% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `assigned` | 1,854,825 | 859,750 | 68.3% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `boiler` | 75,123 | 2,639,452 | 2.8% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `buildingclass` | 2,705,564 | 9,011 | 99.7% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `cityowned` | 229,069 | 2,485,506 | 8.4% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `cluster` | 1,723,718 | 990,857 | 63.5% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `communityboard` | 2,712,643 | 1,932 | 99.9% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `curbcut` | 102,074 | 2,612,501 | 3.8% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `efilingfiled` | 1,643,985 | 1,070,590 | 60.6% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `equipment` | 462,827 | 2,251,748 | 17.0% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `existingdwellingunits` | 985,658 | 1,728,917 | 36.3% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `existingoccupancy` | 1,911,526 | 803,049 | 70.4% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `firealarm` | 126,123 | 2,588,452 | 4.6% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `firesuppression` | 65,907 | 2,648,668 | 2.4% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `fuelburning` | 32,761 | 2,681,814 | 1.2% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `fuelstorage` | 21,783 | 2,692,792 | 0.8% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `fullypaid` | 2,705,205 | 9,370 | 99.7% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `fullypermitted` | 2,012,653 | 701,922 | 74.1% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `gisbin` | 2,677,538 | 37,037 | 98.6% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `giscensustract` | 2,705,730 | 8,845 | 99.7% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `giscouncildistrict` | 2,705,730 | 8,845 | 99.7% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `gislatitude` | 2,705,730 | 8,845 | 99.7% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `gislongitude` | 2,705,730 | 8,845 | 99.7% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `gisntaname` | 2,705,730 | 8,845 | 99.7% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `jobdescription` | 2,423,175 | 291,400 | 89.3% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `landmarked` | 2,541,810 | 172,765 | 93.6% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `littlee` | 1,596,625 | 1,117,950 | 58.8% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `loftboard` | 2,165,174 | 549,401 | 79.8% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `mechanical` | 421,651 | 2,292,924 | 15.5% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `nonprofit` | 2,607,915 | 106,660 | 96.1% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `other` | 1,616,428 | 1,098,147 | 59.5% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `otherdescription` | 1,614,366 | 1,100,209 | 59.5% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `ownersbusinessname` | 2,648,704 | 65,871 | 97.6% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `ownersphone` | 2,695,566 | 19,009 | 99.3% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `ownertype` | 2,605,083 | 109,492 | 96.0% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `paid` | 2,700,457 | 14,118 | 99.5% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `pcfiled` | 926,426 | 1,788,149 | 34.1% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `plumbing` | 841,750 | 1,872,825 | 31.0% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `professionalcert` | 2,136,674 | 577,901 | 78.7% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `proposeddwellingunits` | 1,408,483 | 1,306,092 | 51.9% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `proposedoccupancy` | 1,620,850 | 1,093,725 | 59.7% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `signoffdate` | 1,698,761 | 1,015,814 | 62.6% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `sitefill` | 2,175,435 | 539,140 | 80.1% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `specialactiondate` | 290,836 | 2,423,739 | 10.7% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `specialactionstatus` | 2,683,558 | 31,017 | 98.9% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `specialdistrict1` | 392,077 | 2,322,498 | 14.4% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `specialdistrict2` | 133,210 | 2,581,365 | 4.9% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `sprinkler` | 168,010 | 2,546,565 | 6.2% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `standpipe` | 20,728 | 2,693,847 | 0.8% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `zoningdist1` | 2,196,867 | 517,708 | 80.9% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `zoningdist2` | 288,390 | 2,426,185 | 10.6% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `zoningdist3` | 14,926 | 2,699,649 | 0.5% | Merges into DOB_FILED_PERMIT joined table for frontend display |

#### Always Populated (36 fields)

| Field | Frontend Usage |
|-------|----------------|
| `applicantprofessionaltitle` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `applicantsfirstname` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `applicantslastname` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `bbl` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `bin` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `block` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `borough` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `buildingtype` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `dobrundate` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `doc` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `enlargementsqfootage` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `existingheight` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `existingnoofstories` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `existingzoningsqft` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `feestatus` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `house` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `initialcost` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `job` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `jobnogoodcount` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `jobs1no` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `jobstatus` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `jobstatusdescrp` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `jobtype` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `latestactiondate` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `lot` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `ownersfirstname` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `ownerslastname` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `prefilingdate` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `proposedheight` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `proposednoofstories` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `proposedzoningsqft` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `streetfrontage` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `streetname` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `totalconstructionfloorarea` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `totalestfee` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `withdrawalflag` | Merges into DOB_FILED_PERMIT joined table for frontend display |

---

### `datasets_dobnowfiledpermit`

**Row count:** 884,872

> Note: Merges into DOB_FILED_PERMIT joined table for frontend display

#### Always NULL (66 fields)

| Field | Frontend Usage |
|-------|----------------|
| `antenna` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `applicantsmiddleinitial` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `aptcondonos` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `bin_2` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `boilerequipmentworktype` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `buildingtype` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `built1informationvalue` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `built2ainformationvalue` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `built2binformationvalue` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `built2informationvalue` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `censustract` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `commmunityboard` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `councildistrict` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `curbcut` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `currentstatusdate` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `earthworkworktype` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `exemptfromnycecc` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `existingdwellingunits` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `existingheight` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `existingstories` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `fence` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `filingrepresentativebusinessname` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `filingrepresentativecity` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `filingrepresentativefirstname` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `filingrepresentativelastname` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `filingrepresentativemiddleinitial` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `filingrepresentativestate` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `filingrepresentativestreetname` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `filingrepresentativezip` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `firstpermitdate` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `foundationworktype` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `generalconstructionworktype` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `includespermanentremoval` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `incompliancewithnycecc` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `latitude` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `littlee` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `longitude` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `mechanicalsystemsworktype` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `nta` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `ownerscity` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `ownersstate` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `ownersstreetname` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `ownerszip` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `permitissuedate` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `placeofassemblyworktype` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `plumbingworktype` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `progressinspectionrequirement` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `proposeddwellingunits` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `proposedheight` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `proposednoofstories` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `protectionmechanicalmethodsworktype` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `requestlegalization` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `reviewbuildingcode` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `scaffold` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `shed` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `sidewalkshedworktype` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `sign` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `specialinspectionagencynumber` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `specialinspectionrequirement` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `sprinklerworktype` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `standpipe` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `structuralworktype` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `supportofexcavationworktype` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `temporaryplaceofassemblyworktype` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `totalconstructionfloorarea` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `unmappedccostreet` | Merges into DOB_FILED_PERMIT joined table for frontend display |

#### Partially Populated (6 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `city` | 884,002 | 870 | 99.9% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `filingdate` | 882,381 | 2,491 | 99.7% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `ownersbusinessname` | 829,311 | 55,561 | 93.7% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `state` | 884,002 | 870 | 99.9% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `workonfloor` | 820,342 | 64,530 | 92.7% | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `zip` | 884,002 | 870 | 99.9% | Merges into DOB_FILED_PERMIT joined table for frontend display |

#### Always Populated (15 fields)

| Field | Frontend Usage |
|-------|----------------|
| `applicantfirstname` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `applicantlastname` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `applicantlicense` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `applicantprofessionaltitle` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `bbl` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `bin` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `block` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `borough` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `filingstatus` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `houseno` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `initialcost` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `jobfilingnumber` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `jobtype` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `lot` | Merges into DOB_FILED_PERMIT joined table for frontend display |
| `streetname` | Merges into DOB_FILED_PERMIT joined table for frontend display |

---

### `datasets_dobpermitissuednow`

**Row count:** 916,922

> Note: Merges into DOB_ISSUED_PERMIT joined table for frontend display

#### Always NULL (22 fields)

| Field | Frontend Usage |
|-------|----------------|
| `applicantbusinessaddress` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `applicantbusinessname` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `applicantfirstname` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `applicantlastname` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `applicantlicense` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `applicantmiddlename` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `approveddate` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `aptcondonos` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `cbno` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `estimatedjobcosts` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `filingrepresentativebusinessname` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `filingrepresentativefirstname` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `filingrepresentativelastname` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `filingrepresentativemiddleinitial` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `ownerbusinessname` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `ownercity` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `ownername` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `ownerstate` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `ownerstreetaddress` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `ownerzipcode` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `permitteeslicensetype` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `workonfloor` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |

#### Partially Populated (1 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `expireddate` | 916,139 | 783 | 99.9% | Merges into DOB_ISSUED_PERMIT joined table for frontend display |

#### Always Populated (13 fields)

| Field | Frontend Usage |
|-------|----------------|
| `bbl` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `bin` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `block` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `borough` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `filingreason` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `houseno` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `issueddate` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `jobdescription` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `jobfilingnumber` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `lot` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `streetname` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `workpermit` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |
| `worktype` | Merges into DOB_ISSUED_PERMIT joined table for frontend display |

---

### `datasets_dobviolation`

**Row count:** 2,762,937

#### Partially Populated (10 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `bbl` | 2,746,035 | 16,902 | 99.4% | Not used by frontend |
| `bin` | 2,759,379 | 3,558 | 99.9% | Not used by frontend |
| `block` | 2,748,190 | 14,747 | 99.5% | Not used by frontend |
| `description` | 1,003,153 | 1,759,784 | 36.3% | Table column (Description), expandable |
| `devicenumber` | 2,034,041 | 728,896 | 73.6% | Not used by frontend |
| `dispositioncomments` | 2,050,658 | 712,279 | 74.2% | Not used by frontend |
| `dispositiondate` | 2,100,113 | 662,824 | 76.0% | Not used by frontend |
| `ecbnumber` | 238,621 | 2,524,316 | 8.6% | Not used by frontend |
| `lot` | 2,748,934 | 14,003 | 99.5% | Not used by frontend |
| `street` | 2,743,874 | 19,063 | 99.3% | Not used by frontend |

#### Always Populated (9 fields)

| Field | Frontend Usage |
|-------|----------------|
| `boro` | Not used by frontend |
| `housenumber` | Not used by frontend |
| `isndobbisviol` | Table column (Violation #), link to BIS, keyField |
| `issuedate` | Table column (Date Issued), dateFormatter |
| `number` | Not used by frontend |
| `violationcategory` | Table column (Status), filter buttons (Active/Dismissed) |
| `violationnumber` | Not used by frontend |
| `violationtype` | Table column (Violation Type) |
| `violationtypecode` | Not used by frontend |

---

### `datasets_ecbviolation`

**Row count:** 1,803,653

#### Always NULL (6 fields)

| Field | Frontend Usage |
|-------|----------------|
| `infractioncode10` | Not used by frontend |
| `infractioncode8` | Not used by frontend |
| `infractioncode9` | Not used by frontend |
| `sectionlawdescription10` | Not used by frontend |
| `sectionlawdescription8` | Not used by frontend |
| `sectionlawdescription9` | Not used by frontend |

#### Partially Populated (27 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `aggravatedlevel` | 1,171,558 | 632,095 | 65.0% | Table column (Aggravated Level) |
| `bbl` | 1,776,429 | 27,224 | 98.5% | Not used by frontend |
| `bin` | 1,799,085 | 4,568 | 99.7% | Not used by frontend |
| `block` | 1,776,430 | 27,223 | 98.5% | Not used by frontend |
| `certificationstatus` | 1,698,920 | 104,733 | 94.2% | Not used by frontend |
| `dobviolationnumber` | 1,601,921 | 201,732 | 88.8% | Not used by frontend |
| `hearingstatus` | 1,785,141 | 18,512 | 99.0% | Table column (Hearing Status) |
| `infractioncode2` | 107,585 | 1,696,068 | 6.0% | Not used by frontend |
| `infractioncode3` | 10,463 | 1,793,190 | 0.6% | Not used by frontend |
| `infractioncode4` | 3,729 | 1,799,924 | 0.2% | Not used by frontend |
| `infractioncode5` | 2,074 | 1,801,579 | 0.1% | Not used by frontend |
| `infractioncode6` | 1,336 | 1,802,317 | 0.1% | Not used by frontend |
| `infractioncode7` | 939 | 1,802,714 | 0.1% | Not used by frontend |
| `lot` | 1,776,429 | 27,224 | 98.5% | Not used by frontend |
| `respondentcity` | 1,662,609 | 141,044 | 92.2% | Not used by frontend |
| `respondenthousenumber` | 1,598,953 | 204,700 | 88.7% | Not used by frontend |
| `respondentstreet` | 1,661,020 | 142,633 | 92.1% | Not used by frontend |
| `respondentzip` | 1,621,527 | 182,126 | 89.9% | Not used by frontend |
| `sectionlawdescription1` | 1,790,479 | 13,174 | 99.3% | Table column (Standard Description) |
| `sectionlawdescription2` | 106,337 | 1,697,316 | 5.9% | Not used by frontend |
| `sectionlawdescription3` | 10,408 | 1,793,245 | 0.6% | Not used by frontend |
| `sectionlawdescription4` | 3,717 | 1,799,936 | 0.2% | Not used by frontend |
| `sectionlawdescription5` | 2,068 | 1,801,585 | 0.1% | Not used by frontend |
| `sectionlawdescription6` | 1,334 | 1,802,319 | 0.1% | Not used by frontend |
| `sectionlawdescription7` | 938 | 1,802,715 | 0.1% | Not used by frontend |
| `serveddate` | 1,763,682 | 39,971 | 97.8% | Not used by frontend |
| `violationdescription` | 1,802,529 | 1,124 | 99.9% | Table column (Violation Description), expandable |

#### Always Populated (14 fields)

| Field | Frontend Usage |
|-------|----------------|
| `amountpaid` | Table column (Amount Paid), dollarFormatter |
| `balancedue` | Not used by frontend |
| `boro` | Not used by frontend |
| `ecbviolationnumber` | Table column (Violation #), link to BIS, keyField |
| `ecbviolationstatus` | Table column (Status), filter buttons (Active/Resolved) |
| `hearingdate` | Not used by frontend |
| `hearingtime` | Not used by frontend |
| `infractioncode1` | Not used by frontend |
| `isndobbisextract` | Not used by frontend |
| `issuedate` | Table column (Date Issued), dateFormatter |
| `penalityimposed` | Table column (Penalty Imposed), dollarFormatter |
| `respondentname` | Not used by frontend |
| `severity` | Table column (Severity) |
| `violationtype` | Table column (Violation Type) |

---

### `datasets_eviction`

**Row count:** 108,328

#### Always NULL (3 fields)

| Field | Frontend Usage |
|-------|----------------|
| `evictionzip` | Not used by frontend |
| `geosearch_address` | Not used by frontend |
| `schedulestatus` | Not used by frontend |

#### Partially Populated (11 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `bbl` | 97,997 | 10,331 | 90.5% | Not used by frontend |
| `bin` | 97,996 | 10,332 | 90.5% | Not used by frontend |
| `censustract` | 98,379 | 9,949 | 90.8% | Not used by frontend |
| `cleaned_address` | 6,513 | 101,815 | 6.0% | Not used by frontend |
| `communityboard` | 98,379 | 9,949 | 90.8% | Not used by frontend |
| `councildistrict` | 98,379 | 9,949 | 90.8% | Not used by frontend |
| `evictionapartmentnumber` | 92,429 | 15,899 | 85.3% | Not used by frontend |
| `latitude` | 98,379 | 9,949 | 90.8% | Not used by frontend |
| `longitude` | 98,379 | 9,949 | 90.8% | Not used by frontend |
| `nta` | 98,379 | 9,949 | 90.8% | Not used by frontend |
| `uniqueid` | 6,513 | 101,815 | 6.0% | Not used by frontend |

#### Always Populated (11 fields)

| Field | Frontend Usage |
|-------|----------------|
| `borough` | Not used by frontend |
| `courtindexnumber` | Table column (Court Index #), keyField |
| `docketnumber` | Table column (Docket #) |
| `ejectment` | Not used by frontend |
| `evictionaddress` | Table column (Address), expandable |
| `evictionlegalpossession` | Not used by frontend |
| `evictionpostcode` | Not used by frontend |
| `executeddate` | Table column (Date) |
| `marshal1stname` | Not used by frontend |
| `marshallastname` | Not used by frontend |
| `residentialcommercial` | Not used by frontend |

---

### `datasets_foreclosure`

**Row count:** 56,843

#### Always NULL (1 fields)

| Field | Frontend Usage |
|-------|----------------|
| `mortgage_amount` | Table column (Mortgage Amount), dollarFormatter |

#### Partially Populated (7 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `address` | 52,123 | 4,720 | 91.7% | Not used by frontend |
| `auction` | 6,153 | 50,690 | 10.8% | Not used by frontend |
| `date_added` | 56,761 | 82 | 99.9% | Table column (Date Added) |
| `debtor` | 56,481 | 362 | 99.4% | Table column (Debtor), expandable |
| `document_type` | 54,786 | 2,057 | 96.4% | Table column (Document Type) |
| `lien_type` | 34,420 | 22,423 | 60.6% | Table column (Lien Type) |
| `mortgage_date` | 25,080 | 31,763 | 44.1% | Table column (Mortgage Date) |

#### Always Populated (6 fields)

| Field | Frontend Usage |
|-------|----------------|
| `bbl` | Not used by frontend |
| `creditor` | Table column (Creditor), expandable |
| `foreign_key` | Not used by frontend |
| `index` | Table column (Index #) |
| `key` | Hidden keyField |
| `source` | Table column (Source) |

---

### `datasets_housinglitigation`

**Row count:** 236,872

#### Partially Populated (7 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `bbl` | 236,564 | 308 | 99.9% | Not used by frontend |
| `bin` | 236,564 | 308 | 99.9% | Not used by frontend |
| `caseopendate` | 236,583 | 289 | 99.9% | Table column (Date Open) |
| `findingdate` | 318 | 236,554 | 0.1% | Table column (Finding Date) |
| `findingofharassment` | 8,014 | 228,858 | 3.4% | Table column (Finding of Harassment) |
| `penalty` | 320 | 236,552 | 0.1% | Table column (Penalty) |
| `respondent` | 233,784 | 3,088 | 98.7% | Table column (Respondent) |

#### Always Populated (17 fields)

| Field | Frontend Usage |
|-------|----------------|
| `block` | Not used by frontend |
| `boro` | Not used by frontend |
| `buildingid` | Not used by frontend |
| `casestatus` | Table column (Status) |
| `casetype` | Table column (Case Type) |
| `censustract` | Not used by frontend |
| `communitydistrict` | Not used by frontend |
| `councildistrict` | Not used by frontend |
| `housenumber` | Not used by frontend |
| `latitude` | Not used by frontend |
| `litigationid` | Table column (Litigation ID) |
| `longitude` | Not used by frontend |
| `lot` | Not used by frontend |
| `nta` | Not used by frontend |
| `openjudgement` | Table column (Open Judgement?) |
| `streetname` | Not used by frontend |
| `zip` | Not used by frontend |

---

### `datasets_hpdbuildingrecord`

**Row count:** 380,050

#### Partially Populated (9 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `bbl` | 379,710 | 340 | 99.9% | Not used by frontend |
| `bin` | 367,731 | 12,319 | 96.8% | Not used by frontend |
| `censustract` | 378,934 | 1,116 | 99.7% | Not used by frontend |
| `dobbuildingclass` | 366,149 | 13,901 | 96.3% | Not used by frontend |
| `dobbuildingclassid` | 366,149 | 13,901 | 96.3% | Not used by frontend |
| `legalclassa` | 365,016 | 15,034 | 96.0% | Not used by frontend |
| `legalclassb` | 355,663 | 24,387 | 93.6% | Not used by frontend |
| `legalstories` | 365,259 | 14,791 | 96.1% | Not used by frontend |
| `zip` | 378,907 | 1,143 | 99.7% | Not used by frontend |

#### Always Populated (15 fields)

| Field | Frontend Usage |
|-------|----------------|
| `block` | Not used by frontend |
| `boro` | Not used by frontend |
| `boroid` | Not used by frontend |
| `buildingid` | Not used by frontend |
| `communityboard` | Not used by frontend |
| `highhousenumber` | Not used by frontend |
| `housenumber` | Not used by frontend |
| `lifecycle` | Not used by frontend |
| `lot` | Not used by frontend |
| `lowhousenumber` | Not used by frontend |
| `managementprogram` | Not used by frontend |
| `recordstatus` | Not used by frontend |
| `recordstatusid` | Not used by frontend |
| `registrationid` | Not used by frontend |
| `streetname` | Not used by frontend |

---

### `datasets_hpdcomplaint`

**Row count:** 15,970,576

#### Partially Populated (4 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `bin` | 15,936,791 | 33,785 | 99.8% | Not used by frontend |
| `complaintanonymousflag` | 14,517,389 | 1,453,187 | 90.9% | Not used by frontend |
| `uniquekey` | 13,875,994 | 2,094,582 | 86.9% | Not used by frontend |
| `zip` | 15,962,391 | 8,185 | 99.9% | Not used by frontend |

#### Always Populated (29 fields)

| Field | Frontend Usage |
|-------|----------------|
| `apartment` | Table column (Apt.) |
| `bbl` | Not used by frontend |
| `block` | Not used by frontend |
| `borough` | Not used by frontend |
| `buildingid` | Not used by frontend |
| `census_tract` | Not used by frontend |
| `code` | Table column (Descriptor) |
| `communityboard` | Not used by frontend |
| `complaintid` | Table column (Complaint ID) |
| `council_district` | Not used by frontend |
| `housenumber` | Not used by frontend |
| `latitude` | Not used by frontend |
| `longitude` | Not used by frontend |
| `lot` | Not used by frontend |
| `majorcategory` | Table column (Major Category) |
| `minorcategory` | Table column (Minor Category) |
| `nta` | Not used by frontend |
| `problemduplicateflag` | Not used by frontend |
| `problemid` | Table column (Problem ID), keyField |
| `problemstatus` | Table column (Problem Status) |
| `problemstatusdate` | Not used by frontend |
| `receiveddate` | Table column (Date Received), dateFormatter |
| `spacetype` | Table column (Space Type) |
| `status` | Table column (Status), hpdStatusFormatter, filter buttons (Open/Closed) |
| `statusdate` | Not used by frontend |
| `statusdescription` | Table column (Status Description) |
| `streetname` | Not used by frontend |
| `type` | Table column (Urgency) |
| `unittype` | Not used by frontend |

---

### `datasets_hpdcontact`

**Row count:** 731,030

#### Partially Populated (12 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `businessapartment` | 252,034 | 478,996 | 34.5% | Not used by frontend |
| `businesscity` | 573,689 | 157,341 | 78.5% | Not used by frontend |
| `businesshousenumber` | 573,393 | 157,637 | 78.4% | Not used by frontend |
| `businessstate` | 572,669 | 158,361 | 78.3% | Not used by frontend |
| `businessstreetname` | 573,534 | 157,496 | 78.5% | Not used by frontend |
| `businesszip` | 573,354 | 157,676 | 78.4% | Not used by frontend |
| `contactdescription` | 729,917 | 1,113 | 99.8% | Not used by frontend |
| `corporationname` | 191,624 | 539,406 | 26.2% | Not used by frontend |
| `firstname` | 616,803 | 114,227 | 84.4% | Not used by frontend |
| `lastname` | 616,310 | 114,720 | 84.3% | Not used by frontend |
| `middleinitial` | 99,428 | 631,602 | 13.6% | Not used by frontend |
| `title` | 119,589 | 611,441 | 16.4% | Not used by frontend |

#### Always Populated (3 fields)

| Field | Frontend Usage |
|-------|----------------|
| `registrationcontactid` | Not used by frontend |
| `registrationid` | Not used by frontend |
| `type` | Not used by frontend |

---

### `datasets_hpdregistration`

**Row count:** 193,881

#### Partially Populated (1 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `lastregistrationdate` | 190,637 | 3,244 | 98.3% | Not used by frontend |

#### Always Populated (16 fields)

| Field | Frontend Usage |
|-------|----------------|
| `bbl` | Not used by frontend |
| `bin` | Not used by frontend |
| `block` | Not used by frontend |
| `boro` | Not used by frontend |
| `boroid` | Not used by frontend |
| `buildingid` | Not used by frontend |
| `communityboard` | Not used by frontend |
| `highhousenumber` | Not used by frontend |
| `housenumber` | Not used by frontend |
| `lot` | Not used by frontend |
| `lowhousenumber` | Not used by frontend |
| `registrationenddate` | Not used by frontend |
| `registrationid` | Not used by frontend |
| `streetcode` | Not used by frontend |
| `streetname` | Not used by frontend |
| `zip` | Not used by frontend |

---

### `datasets_hpdviolation`

**Row count:** 10,802,593

#### Partially Populated (19 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `apartment` | 7,239,567 | 3,563,026 | 67.0% | Table column (Apartment) |
| `bbl` | 10,784,347 | 18,246 | 99.8% | Not used by frontend |
| `bin` | 10,784,347 | 18,246 | 99.8% | Not used by frontend |
| `censustract` | 10,794,449 | 8,144 | 99.9% | Not used by frontend |
| `certifieddate` | 3,825,263 | 6,977,330 | 35.4% | Not used by frontend |
| `communityboard` | 10,794,449 | 8,144 | 99.9% | Not used by frontend |
| `councildistrict` | 10,794,449 | 8,144 | 99.9% | Not used by frontend |
| `latitude` | 10,794,449 | 8,144 | 99.9% | Not used by frontend |
| `longitude` | 10,794,449 | 8,144 | 99.9% | Not used by frontend |
| `newcertifybydate` | 92,930 | 10,709,663 | 0.9% | Not used by frontend |
| `newcorrectbydate` | 92,930 | 10,709,663 | 0.9% | Not used by frontend |
| `novid` | 9,992,403 | 810,190 | 92.5% | Not used by frontend |
| `novissueddate` | 9,989,854 | 812,739 | 92.5% | Not used by frontend |
| `novtype` | 9,992,399 | 810,194 | 92.5% | Not used by frontend |
| `nta` | 10,794,449 | 8,144 | 99.9% | Not used by frontend |
| `originalcertifybydate` | 9,989,854 | 812,739 | 92.5% | Not used by frontend |
| `originalcorrectbydate` | 9,989,816 | 812,777 | 92.5% | Not used by frontend |
| `postcode` | 10,794,223 | 8,370 | 99.9% | Not used by frontend |
| `story` | 8,953,482 | 1,849,111 | 82.9% | Table column (Floor) |

#### Always Populated (22 fields)

| Field | Frontend Usage |
|-------|----------------|
| `approveddate` | Table column (Date Approved), dateFormatter |
| `block` | Not used by frontend |
| `boroid` | Not used by frontend |
| `borough` | Not used by frontend |
| `buildingid` | Not used by frontend |
| `class_name` | Table column (Class), filter buttons (A/B/C) |
| `currentstatus` | Not used by frontend |
| `currentstatusdate` | Not used by frontend |
| `currentstatusid` | Not used by frontend |
| `highhousenumber` | Not used by frontend |
| `housenumber` | Not used by frontend |
| `inspectiondate` | Not used by frontend |
| `lot` | Not used by frontend |
| `lowhousenumber` | Not used by frontend |
| `novdescription` | Table column (Description), expandable |
| `ordernumber` | Not used by frontend |
| `registrationid` | Not used by frontend |
| `rentimpairing` | Not used by frontend |
| `streetcode` | Not used by frontend |
| `streetname` | Not used by frontend |
| `violationid` | Table column (Violation ID) |
| `violationstatus` | Table column (Status), hpdStatusFormatter, filter buttons (Open/Closed) |

---

### `datasets_lispenden`

**Row count:** 13,295

#### Always NULL (1 fields)

| Field | Frontend Usage |
|-------|----------------|
| `thirdparty` | Not used by frontend |

#### Partially Populated (9 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `attorney` | 4,067 | 9,228 | 30.6% | Not used by frontend |
| `bc` | 13,284 | 11 | 99.9% | Not used by frontend |
| `debtor` | 9,566 | 3,729 | 72.0% | Table column (Debtor), expandable |
| `disp` | 1,661 | 11,634 | 12.5% | Not used by frontend |
| `satdate` | 4,142 | 9,153 | 31.2% | Not used by frontend |
| `sattype` | 8,208 | 5,087 | 61.7% | Not used by frontend |
| `source` | 4,063 | 9,232 | 30.6% | Not used by frontend |
| `type` | 8,939 | 4,356 | 67.2% | Not used by frontend |
| `zip` | 13,284 | 11 | 99.9% | Not used by frontend |

#### Always Populated (6 fields)

| Field | Frontend Usage |
|-------|----------------|
| `bbl` | Not used by frontend |
| `cr` | Table column (Creditor), expandable |
| `entereddate` | Not used by frontend |
| `fileddate` | Table column (Date Filed) |
| `index` | Not used by frontend |
| `key` | Hidden keyField |

---

### `datasets_lispendencomment`

**Row count:** 87,306

#### Always Populated (2 fields)

| Field | Frontend Usage |
|-------|----------------|
| `datecomments` | Not used by frontend |
| `key` | Not used by frontend |

---

### `datasets_ocahousingcourt`

**Row count:** 2,259,564

#### Always NULL (13 fields)

| Field | Frontend Usage |
|-------|----------------|
| `bin` | Not used by frontend |
| `boroughcode` | Not used by frontend |
| `dateofjurydemand` | Not used by frontend |
| `hnum` | Not used by frontend |
| `housenumber` | Not used by frontend |
| `lat` | Not used by frontend |
| `lng` | Not used by frontend |
| `lon` | Not used by frontend |
| `placename` | Not used by frontend |
| `sname` | Not used by frontend |
| `street1` | Not used by frontend |
| `street2` | Not used by frontend |
| `streetname` | Not used by frontend |

#### Partially Populated (18 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `bbl` | 1,289,754 | 969,810 | 57.1% | Not used by frontend |
| `bct2020` | 1,612,773 | 646,791 | 71.4% | Not used by frontend |
| `bctcb2020` | 1,612,773 | 646,791 | 71.4% | Not used by frontend |
| `boro` | 1,675,677 | 583,887 | 74.2% | Not used by frontend |
| `cb2010` | 1,612,773 | 646,791 | 71.4% | Not used by frontend |
| `cd` | 1,622,167 | 637,397 | 71.8% | Not used by frontend |
| `council` | 1,622,167 | 637,397 | 71.8% | Not used by frontend |
| `ct` | 1,612,773 | 646,791 | 71.4% | Not used by frontend |
| `ct2010` | 1,612,773 | 646,791 | 71.4% | Not used by frontend |
| `disposeddate` | 2,071,143 | 188,421 | 91.7% | Table column (Disposed Date) |
| `disposedreason` | 2,071,143 | 188,421 | 91.7% | Table column (Disposed Reason), expandable |
| `grc` | 2,221,132 | 38,432 | 98.3% | Not used by frontend |
| `grc2` | 2,221,132 | 38,432 | 98.3% | Not used by frontend |
| `msg` | 661,319 | 1,598,245 | 29.3% | Not used by frontend |
| `msg2` | 823,019 | 1,436,545 | 36.4% | Not used by frontend |
| `propertytype` | 1,903,752 | 355,812 | 84.3% | Table column (Property Type) |
| `specialtydesignationtypes` | 1,249,502 | 1,010,062 | 55.3% | Not used by frontend |
| `unitsres` | 1,612,473 | 647,091 | 71.4% | Not used by frontend |

#### Always Populated (10 fields)

| Field | Frontend Usage |
|-------|----------------|
| `city` | Not used by frontend |
| `classification` | Table column (Case Type) |
| `court` | Table column (Court) |
| `fileddate` | Table column (Filed Date) |
| `firstpaper` | Not used by frontend |
| `indexnumberid` | Hidden keyField |
| `postalcode` | Not used by frontend |
| `primaryclaimtotal` | Not used by frontend |
| `state` | Not used by frontend |
| `status` | Table column (Status) |

---

### `datasets_padrecord`

**Row count:** 1,236,507

#### Always NULL (2 fields)

| Field | Frontend Usage |
|-------|----------------|
| `dapsflag` | Infrastructure/lookup - not directly displayed |
| `naubflag` | Infrastructure/lookup - not directly displayed |

#### Partially Populated (10 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `addrtype` | 11,136 | 1,225,371 | 0.9% | Infrastructure/lookup - not directly displayed |
| `hcontpar` | 7,396 | 1,229,111 | 0.6% | Infrastructure/lookup - not directly displayed |
| `hsos` | 1,234,337 | 2,170 | 99.8% | Infrastructure/lookup - not directly displayed |
| `lcontpar` | 7,396 | 1,229,111 | 0.6% | Infrastructure/lookup - not directly displayed |
| `lsos` | 1,234,259 | 2,248 | 99.8% | Infrastructure/lookup - not directly displayed |
| `physicalid` | 1,206,145 | 30,362 | 97.5% | Infrastructure/lookup - not directly displayed |
| `realb7sc` | 1,242 | 1,235,265 | 0.1% | Infrastructure/lookup - not directly displayed |
| `segid` | 1,234,488 | 2,019 | 99.8% | Infrastructure/lookup - not directly displayed |
| `validlgcs` | 1,235,399 | 1,108 | 99.9% | Infrastructure/lookup - not directly displayed |
| `zipcode` | 1,234,486 | 2,021 | 99.8% | Infrastructure/lookup - not directly displayed |

#### Always Populated (16 fields)

| Field | Frontend Usage |
|-------|----------------|
| `b10sc` | Infrastructure/lookup - not directly displayed |
| `bbl` | Infrastructure/lookup - not directly displayed |
| `bin` | Infrastructure/lookup - not directly displayed |
| `block` | Infrastructure/lookup - not directly displayed |
| `boro` | Infrastructure/lookup - not directly displayed |
| `hhnd` | Infrastructure/lookup - not directly displayed |
| `hhns` | Infrastructure/lookup - not directly displayed |
| `key` | Infrastructure/lookup - not directly displayed |
| `lhnd` | Infrastructure/lookup - not directly displayed |
| `lhns` | Infrastructure/lookup - not directly displayed |
| `lot` | Infrastructure/lookup - not directly displayed |
| `parity` | Infrastructure/lookup - not directly displayed |
| `sc5` | Infrastructure/lookup - not directly displayed |
| `scboro` | Infrastructure/lookup - not directly displayed |
| `sclgc` | Infrastructure/lookup - not directly displayed |
| `stname` | Infrastructure/lookup - not directly displayed |

---

### `datasets_property`

**Row count:** 872,840

#### Always NULL (10 fields)

| Field | Frontend Usage |
|-------|----------------|
| `mapplutof` | Not used by frontend |
| `masdate` | Not used by frontend |
| `newnotinold` | Not used by frontend |
| `notes` | Not used by frontend |
| `overlay2` | Zoning section |
| `polidate` | Not used by frontend |
| `spdist2` | Zoning section |
| `spdist3` | Zoning section |
| `zonedist3` | Zoning section |
| `zonedist4` | Zoning section |

#### Partially Populated (92 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `address` | 871,945 | 895 | 99.9% | Profile header |
| `appbbl` | 104,785 | 768,055 | 12.0% | Not used by frontend |
| `appdate` | 101,547 | 771,293 | 11.6% | Not used by frontend |
| `areasource` | 872,181 | 659 | 99.9% | Not used by frontend |
| `assessland` | 872,181 | 659 | 99.9% | Not used by frontend |
| `assesstot` | 872,181 | 659 | 99.9% | Not used by frontend |
| `basempdate` | 2,438 | 870,402 | 0.3% | Not used by frontend |
| `bct2020` | 859,908 | 12,932 | 98.5% | Not used by frontend |
| `bctcb2020` | 859,906 | 12,934 | 98.5% | Not used by frontend |
| `bldgarea` | 872,110 | 730 | 99.9% | Not used by frontend |
| `bldgclass` | 872,071 | 769 | 99.9% | Not used by frontend |
| `bldgdepth` | 866,709 | 6,131 | 99.3% | Not used by frontend |
| `bldgfront` | 866,709 | 6,131 | 99.3% | Not used by frontend |
| `borough` | 861,660 | 11,180 | 98.7% | Location section, Maps link |
| `bsmtcode` | 872,069 | 771 | 99.9% | Not used by frontend |
| `builtfar` | 866,297 | 6,543 | 99.3% | Zoning section |
| `cb2010` | 866,328 | 6,512 | 99.3% | Not used by frontend |
| `cd` | 858,113 | 14,727 | 98.3% | Profile info |
| `censustract2010` | 859,280 | 13,560 | 98.4% | Not used by frontend |
| `comarea` | 821,114 | 51,726 | 94.1% | Not used by frontend |
| `condono` | 14,487 | 858,353 | 1.7% | Not used by frontend |
| `council` | 858,778 | 14,062 | 98.4% | Profile info |
| `councildistrict` | 857,720 | 15,120 | 98.3% | Not used by frontend |
| `ct2010` | 865,154 | 7,686 | 99.1% | Not used by frontend |
| `dcasdate` | 2,438 | 870,402 | 0.3% | Not used by frontend |
| `dcpedited` | 42,058 | 830,782 | 4.8% | Not used by frontend |
| `easements` | 872,181 | 659 | 99.9% | Not used by frontend |
| `edesigdate` | 2,438 | 870,402 | 0.3% | Not used by frontend |
| `edesignum` | 11,574 | 861,266 | 1.3% | Not used by frontend |
| `exemptland` | 861,201 | 11,639 | 98.7% | Not used by frontend |
| `exempttot` | 872,181 | 659 | 99.9% | Not used by frontend |
| `ext` | 797,198 | 75,642 | 91.3% | Not used by frontend |
| `factryarea` | 821,114 | 51,726 | 94.1% | Not used by frontend |
| `firecomp` | 866,211 | 6,629 | 99.2% | Not used by frontend |
| `firm07flag` | 35,052 | 837,788 | 4.0% | Not used by frontend |
| `garagearea` | 821,114 | 51,726 | 94.1% | Not used by frontend |
| `geom` | 2,572 | 870,268 | 0.3% | Not used by frontend |
| `healtharea` | 866,236 | 6,604 | 99.2% | Not used by frontend |
| `healthcenterdistrict` | 866,248 | 6,592 | 99.2% | Not used by frontend |
| `histdist` | 31,727 | 841,113 | 3.6% | Not used by frontend |
| `irrlotcode` | 872,069 | 771 | 99.9% | Not used by frontend |
| `landmark` | 1,494 | 871,346 | 0.2% | Not used by frontend |
| `landmkdate` | 2,438 | 870,402 | 0.3% | Not used by frontend |
| `landuse` | 869,475 | 3,365 | 99.6% | Not used by frontend |
| `lat` | 861,210 | 11,630 | 98.7% | Not used by frontend |
| `latitude` | 862,590 | 10,250 | 98.8% | Map component |
| `lng` | 861,210 | 11,630 | 98.7% | Not used by frontend |
| `longitude` | 862,590 | 10,250 | 98.8% | Map component |
| `lotarea` | 866,709 | 6,131 | 99.3% | Not used by frontend |
| `lotdepth` | 866,704 | 6,136 | 99.3% | Not used by frontend |
| `lotfront` | 866,709 | 6,131 | 99.3% | Not used by frontend |
| `lottype` | 872,069 | 771 | 99.9% | Not used by frontend |
| `ltdheight` | 3,069 | 869,771 | 0.4% | Not used by frontend |
| `numbldgs` | 866,712 | 6,128 | 99.3% | Not used by frontend |
| `numfloors` | 824,102 | 48,738 | 94.4% | Not used by frontend |
| `officearea` | 821,114 | 51,726 | 94.1% | Not used by frontend |
| `original_address` | 869,396 | 3,444 | 99.6% | Not used by frontend |
| `otherarea` | 821,114 | 51,726 | 94.1% | Not used by frontend |
| `overlay1` | 75,348 | 797,492 | 8.6% | Zoning section |
| `ownername` | 866,495 | 6,345 | 99.3% | Ownership section |
| `ownertype` | 41,363 | 831,477 | 4.7% | Not used by frontend |
| `pfirm15flag` | 66,239 | 806,601 | 7.6% | Not used by frontend |
| `policeprct` | 866,239 | 6,601 | 99.2% | Not used by frontend |
| `proxcode` | 872,069 | 771 | 99.9% | Not used by frontend |
| `resarea` | 821,114 | 51,726 | 94.1% | Not used by frontend |
| `retailarea` | 821,114 | 51,726 | 94.1% | Not used by frontend |
| `rpaddate` | 2,438 | 870,402 | 0.3% | Not used by frontend |
| `sanborn` | 864,021 | 8,819 | 99.0% | Not used by frontend |
| `sanitboro` | 865,975 | 6,865 | 99.2% | Not used by frontend |
| `sanitdistrict` | 865,975 | 6,865 | 99.2% | Not used by frontend |
| `sanitsub` | 865,829 | 7,011 | 99.2% | Not used by frontend |
| `schooldist` | 866,244 | 6,596 | 99.2% | Not used by frontend |
| `spdist1` | 109,406 | 763,434 | 12.5% | Zoning section |
| `splitzone` | 862,298 | 10,542 | 98.8% | Not used by frontend |
| `stateassembly` | 862,152 | 10,688 | 98.8% | Profile info |
| `statesenate` | 862,413 | 10,427 | 98.8% | Profile info |
| `strgearea` | 821,114 | 51,726 | 94.1% | Not used by frontend |
| `taxmap` | 864,021 | 8,819 | 99.0% | Not used by frontend |
| `tract2010` | 867,290 | 5,550 | 99.4% | Not used by frontend |
| `unitsres` | 872,060 | 780 | 99.9% | Profile info |
| `unitstotal` | 872,061 | 779 | 99.9% | Profile info |
| `xcoord` | 865,099 | 7,741 | 99.1% | Not used by frontend |
| `ycoord` | 865,099 | 7,741 | 99.1% | Not used by frontend |
| `yearalter1` | 872,181 | 659 | 99.9% | Not used by frontend |
| `yearalter2` | 872,181 | 659 | 99.9% | Not used by frontend |
| `yearbuilt` | 872,181 | 659 | 99.9% | Profile info |
| `zipcode` | 857,370 | 15,470 | 98.2% | Profile info |
| `zmcode` | 15,724 | 857,116 | 1.8% | Not used by frontend |
| `zonedist1` | 862,296 | 10,544 | 98.8% | Zoning section |
| `zonedist2` | 20,017 | 852,823 | 2.3% | Zoning section |
| `zonemap` | 862,430 | 10,410 | 98.8% | Not used by frontend |
| `zoningdate` | 2,438 | 870,402 | 0.3% | Not used by frontend |

#### Always Populated (9 fields)

| Field | Frontend Usage |
|-------|----------------|
| `bbl` | Profile header, URL routing, keyField |
| `block` | Not used by frontend |
| `borocode` | Not used by frontend |
| `commfar` | Zoning section |
| `facilfar` | Zoning section |
| `lot` | Not used by frontend |
| `plutomapid` | Not used by frontend |
| `residfar` | Zoning section |
| `version` | Not used by frontend |

---

### `datasets_propertyannotation`

**Row count:** 872,840

#### Partially Populated (7 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `aepdischargedate` | 2,765 | 870,075 | 0.3% | Not used by frontend |
| `aepstartdate` | 3,640 | 869,200 | 0.4% | Not used by frontend |
| `latestsaledate` | 710,799 | 162,041 | 81.4% | Not used by frontend |
| `latestsaleprice` | 710,799 | 162,041 | 81.4% | Not used by frontend |
| `legalclassa` | 336,321 | 536,519 | 38.5% | Not used by frontend |
| `legalclassb` | 330,163 | 542,677 | 37.8% | Not used by frontend |
| `subsidyprograms` | 21,079 | 851,761 | 2.4% | Not used by frontend |

#### Always Populated (57 fields)

| Field | Frontend Usage |
|-------|----------------|
| `acrisrealmasters_last30` | Not used by frontend |
| `acrisrealmasters_last3years` | Not used by frontend |
| `acrisrealmasters_lastupdated` | Not used by frontend |
| `acrisrealmasters_lastyear` | Not used by frontend |
| `aepstatus` | Not used by frontend |
| `bbl` | Not used by frontend |
| `conhrecord` | Not used by frontend |
| `dobcomplaints_last30` | Not used by frontend |
| `dobcomplaints_last3years` | Not used by frontend |
| `dobcomplaints_lastupdated` | Not used by frontend |
| `dobcomplaints_lastyear` | Not used by frontend |
| `dobfiledpermits_last30` | Not used by frontend |
| `dobfiledpermits_last3years` | Not used by frontend |
| `dobfiledpermits_lastupdated` | Not used by frontend |
| `dobfiledpermits_lastyear` | Not used by frontend |
| `dobissuedpermits_last30` | Not used by frontend |
| `dobissuedpermits_last3years` | Not used by frontend |
| `dobissuedpermits_lastupdated` | Not used by frontend |
| `dobissuedpermits_lastyear` | Not used by frontend |
| `dobviolations_last30` | Not used by frontend |
| `dobviolations_last3years` | Not used by frontend |
| `dobviolations_lastupdated` | Not used by frontend |
| `dobviolations_lastyear` | Not used by frontend |
| `ecbviolations_last30` | Not used by frontend |
| `ecbviolations_last3years` | Not used by frontend |
| `ecbviolations_lastupdated` | Not used by frontend |
| `ecbviolations_lastyear` | Not used by frontend |
| `evictions_last30` | Not used by frontend |
| `evictions_last3years` | Not used by frontend |
| `evictions_lastupdated` | Not used by frontend |
| `evictions_lastyear` | Not used by frontend |
| `foreclosures_last30` | Not used by frontend |
| `foreclosures_last3years` | Not used by frontend |
| `foreclosures_lastupdated` | Not used by frontend |
| `foreclosures_lastyear` | Not used by frontend |
| `housinglitigations_last30` | Not used by frontend |
| `housinglitigations_last3years` | Not used by frontend |
| `housinglitigations_lastupdated` | Not used by frontend |
| `housinglitigations_lastyear` | Not used by frontend |
| `hpdcomplaints_last30` | Not used by frontend |
| `hpdcomplaints_last3years` | Not used by frontend |
| `hpdcomplaints_lastupdated` | Not used by frontend |
| `hpdcomplaints_lastyear` | Not used by frontend |
| `hpdviolations_last30` | Not used by frontend |
| `hpdviolations_last3years` | Not used by frontend |
| `hpdviolations_lastupdated` | Not used by frontend |
| `hpdviolations_lastyear` | Not used by frontend |
| `managementprogram` | Not used by frontend |
| `nycha` | Not used by frontend |
| `ocahousingcourts_last30` | Not used by frontend |
| `ocahousingcourts_last3years` | Not used by frontend |
| `ocahousingcourts_lastupdated` | Not used by frontend |
| `ocahousingcourts_lastyear` | Not used by frontend |
| `subsidy421a` | Not used by frontend |
| `subsidyj51` | Not used by frontend |
| `taxlien` | Not used by frontend |
| `unitsrentstabilized` | Not used by frontend |

---

### `datasets_psforeclosure`

**Row count:** 14,439

#### Always NULL (1 fields)

| Field | Frontend Usage |
|-------|----------------|
| `bldgareasqft` | Not used by frontend |

#### Partially Populated (12 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `buildingclass` | 14,395 | 44 | 99.7% | Not used by frontend |
| `hasphoto` | 12,943 | 1,496 | 89.6% | Not used by frontend |
| `indexno` | 13,545 | 894 | 93.8% | Table column (Index No.) |
| `judgment` | 13,403 | 1,036 | 92.8% | Not used by frontend |
| `legalprocess` | 7,211 | 7,228 | 49.9% | Not used by frontend |
| `lien` | 11,839 | 2,600 | 82.0% | Table column (Lien Amount), dollarFormatter |
| `neighborhood` | 14,409 | 30 | 99.8% | Not used by frontend |
| `plaintiffsattorney` | 14,353 | 86 | 99.4% | Not used by frontend |
| `referee` | 13,427 | 1,012 | 93.0% | Not used by frontend |
| `schooldistrict` | 14,365 | 74 | 99.5% | Not used by frontend |
| `unitnumber` | 2,362 | 12,077 | 16.4% | Not used by frontend |
| `zipcode` | 14,346 | 93 | 99.4% | Not used by frontend |

#### Always Populated (10 fields)

| Field | Frontend Usage |
|-------|----------------|
| `address` | Not used by frontend |
| `auction` | Table column (Auction Date) |
| `auctionlocation` | Table column (Auction Location), expandable |
| `auctiontime` | Not used by frontend |
| `bbl` | Not used by frontend |
| `dateadded` | Table column (Date Added) |
| `defendant` | Table column (Defendant), expandable |
| `foreclosuretype` | Table column (Foreclosure Type) |
| `key` | Hidden keyField |
| `plaintiff` | Table column (Plaintiff), expandable |

---

### `datasets_pspreforeclosure`

**Row count:** 52,123

#### Always NULL (2 fields)

| Field | Frontend Usage |
|-------|----------------|
| `bldgareasqft` | Not used by frontend |
| `mortgageamount` | Not used by frontend |

#### Partially Populated (11 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `buildingclass` | 41,127 | 10,996 | 78.9% | Not used by frontend |
| `debtoraddress` | 8,694 | 43,429 | 16.7% | Not used by frontend |
| `documenttype` | 49,803 | 2,320 | 95.5% | Not used by frontend |
| `effectivedate` | 45,344 | 6,779 | 87.0% | Not used by frontend |
| `hasphoto` | 46,805 | 5,318 | 89.8% | Not used by frontend |
| `lientype` | 34,853 | 17,270 | 66.9% | Not used by frontend |
| `mortgagedate` | 27,593 | 24,530 | 52.9% | Not used by frontend |
| `neighborhood` | 50,675 | 1,448 | 97.2% | Not used by frontend |
| `schooldistrict` | 51,157 | 966 | 98.1% | Not used by frontend |
| `taxvalue` | 51,272 | 851 | 98.4% | Not used by frontend |
| `zipcode` | 51,716 | 407 | 99.2% | Not used by frontend |

#### Always Populated (7 fields)

| Field | Frontend Usage |
|-------|----------------|
| `address` | Not used by frontend |
| `bbl` | Not used by frontend |
| `creditor` | Not used by frontend |
| `dateadded` | Not used by frontend |
| `debtor` | Not used by frontend |
| `indexno` | Not used by frontend |
| `key` | Not used by frontend |

---

### `datasets_publichousingrecord`

**Row count:** 4,519

#### Partially Populated (1 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `facility` | 2,124 | 2,395 | 47.0% | Not used by frontend |

#### Always Populated (9 fields)

| Field | Frontend Usage |
|-------|----------------|
| `address` | Not used by frontend |
| `bbl` | Not used by frontend |
| `block` | Not used by frontend |
| `borough` | Not used by frontend |
| `cd` | Not used by frontend |
| `development` | Not used by frontend |
| `lot` | Not used by frontend |
| `managedby` | Not used by frontend |
| `zipcode` | Not used by frontend |

---

### `datasets_rentstabilizationrecord`

**Row count:** 52,172

#### Always NULL (34 fields)

| Field | Frontend Usage |
|-------|----------------|
| `abat2007` | Not used by frontend |
| `abat2008` | Not used by frontend |
| `abat2018` | Not used by frontend |
| `abat2019` | Not used by frontend |
| `abat2020` | Not used by frontend |
| `abat2021` | Not used by frontend |
| `abat2022` | Not used by frontend |
| `abat2023` | Not used by frontend |
| `abat2024` | Not used by frontend |
| `dhcr2007` | Not used by frontend |
| `dhcr2008` | Not used by frontend |
| `dhcr2010` | Not used by frontend |
| `dhcr2014` | Not used by frontend |
| `dhcr2015` | Not used by frontend |
| `dhcr2016` | Not used by frontend |
| `dhcr2017` | Not used by frontend |
| `dhcr2018` | Not used by frontend |
| `dhcr2019` | Not used by frontend |
| `dhcr2020` | Not used by frontend |
| `dhcr2021` | Not used by frontend |
| `dhcr2022` | Not used by frontend |
| `dhcr2023` | Not used by frontend |
| `dhcr2024` | Not used by frontend |
| `est2018` | Not used by frontend |
| `est2019` | Not used by frontend |
| `est2020` | Not used by frontend |
| `est2021` | Not used by frontend |
| `est2022` | Not used by frontend |
| `est2023` | Not used by frontend |
| `est2024` | Not used by frontend |
| `uc2024` | Not used by frontend |
| `uc2025` | Not used by frontend |
| `uc2026` | Not used by frontend |
| `uc2027` | Not used by frontend |

#### Partially Populated (60 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `abat2009` | 22,422 | 29,750 | 43.0% | Not used by frontend |
| `abat2010` | 22,868 | 29,304 | 43.8% | Not used by frontend |
| `abat2011` | 23,213 | 28,959 | 44.5% | Not used by frontend |
| `abat2012` | 23,295 | 28,877 | 44.7% | Not used by frontend |
| `abat2013` | 23,887 | 28,285 | 45.8% | Not used by frontend |
| `abat2014` | 21,997 | 30,175 | 42.2% | Not used by frontend |
| `abat2015` | 12,374 | 39,798 | 23.7% | Not used by frontend |
| `abat2016` | 11,286 | 40,886 | 21.6% | Not used by frontend |
| `abat2017` | 22,531 | 29,641 | 43.2% | Not used by frontend |
| `address` | 46,113 | 6,059 | 88.4% | Not used by frontend |
| `borough` | 46,120 | 6,052 | 88.4% | Not used by frontend |
| `cb2010` | 46,089 | 6,083 | 88.3% | Not used by frontend |
| `cd` | 46,120 | 6,052 | 88.4% | Not used by frontend |
| `condono` | 46,120 | 6,052 | 88.4% | Not used by frontend |
| `council` | 46,113 | 6,059 | 88.4% | Not used by frontend |
| `ct2010` | 46,113 | 6,059 | 88.4% | Not used by frontend |
| `dhcr2009` | 36,519 | 15,653 | 70.0% | Not used by frontend |
| `dhcr2011` | 36,097 | 16,075 | 69.2% | Not used by frontend |
| `dhcr2012` | 37,899 | 14,273 | 72.6% | Not used by frontend |
| `dhcr2013` | 38,100 | 14,072 | 73.0% | Not used by frontend |
| `est2007` | 46,461 | 5,711 | 89.1% | Not used by frontend |
| `est2008` | 46,461 | 5,711 | 89.1% | Not used by frontend |
| `est2009` | 46,461 | 5,711 | 89.1% | Not used by frontend |
| `est2010` | 46,461 | 5,711 | 89.1% | Not used by frontend |
| `est2011` | 46,461 | 5,711 | 89.1% | Not used by frontend |
| `est2012` | 46,461 | 5,711 | 89.1% | Not used by frontend |
| `est2013` | 46,461 | 5,711 | 89.1% | Not used by frontend |
| `est2014` | 46,461 | 5,711 | 89.1% | Not used by frontend |
| `est2015` | 46,461 | 5,711 | 89.1% | Not used by frontend |
| `est2016` | 46,461 | 5,711 | 89.1% | Not used by frontend |
| `est2017` | 46,461 | 5,711 | 89.1% | Not used by frontend |
| `lat` | 45,842 | 6,330 | 87.9% | Not used by frontend |
| `latestuctotals` | 38,225 | 13,947 | 73.3% | Not used by frontend |
| `lon` | 45,842 | 6,330 | 87.9% | Not used by frontend |
| `numbldgs` | 46,120 | 6,052 | 88.4% | Not used by frontend |
| `numfloors` | 46,120 | 6,052 | 88.4% | Not used by frontend |
| `ownername` | 45,607 | 6,565 | 87.4% | Not used by frontend |
| `pdfsoa2018` | 42,674 | 9,498 | 81.8% | Not used by frontend |
| `pdfsoa2019` | 50,245 | 1,927 | 96.3% | Not used by frontend |
| `uc2007` | 41,050 | 11,122 | 78.7% | Not used by frontend |
| `uc2008` | 41,050 | 11,122 | 78.7% | Not used by frontend |
| `uc2009` | 38,434 | 13,738 | 73.7% | Not used by frontend |
| `uc2010` | 38,070 | 14,102 | 73.0% | Not used by frontend |
| `uc2011` | 38,983 | 13,189 | 74.7% | Not used by frontend |
| `uc2012` | 39,759 | 12,413 | 76.2% | Not used by frontend |
| `uc2013` | 39,868 | 12,304 | 76.4% | Not used by frontend |
| `uc2014` | 38,893 | 13,279 | 74.5% | Not used by frontend |
| `uc2015` | 38,275 | 13,897 | 73.4% | Not used by frontend |
| `uc2016` | 38,039 | 14,133 | 72.9% | Not used by frontend |
| `uc2017` | 37,709 | 14,463 | 72.3% | Not used by frontend |
| `uc2018` | 40,221 | 11,951 | 77.1% | Not used by frontend |
| `uc2019` | 37,836 | 14,336 | 72.5% | Not used by frontend |
| `uc2020` | 29,427 | 22,745 | 56.4% | Not used by frontend |
| `uc2021` | 29,389 | 22,783 | 56.3% | Not used by frontend |
| `uc2022` | 28,258 | 23,914 | 54.2% | Not used by frontend |
| `uc2023` | 46,301 | 5,871 | 88.7% | Not used by frontend |
| `unitsres` | 46,120 | 6,052 | 88.4% | Not used by frontend |
| `unitstotal` | 46,120 | 6,052 | 88.4% | Not used by frontend |
| `yearbuilt` | 46,120 | 6,052 | 88.4% | Not used by frontend |
| `zipcode` | 46,112 | 6,060 | 88.4% | Not used by frontend |

#### Always Populated (1 fields)

| Field | Frontend Usage |
|-------|----------------|
| `ucbbl` | Not used by frontend |

---

### `datasets_stateassembly`

**Row count:** 65

#### Always Populated (1 fields)

| Field | Frontend Usage |
|-------|----------------|
| `data` | Infrastructure/lookup - not directly displayed |

---

### `datasets_statesenate`

**Row count:** 28

#### Always Populated (1 fields)

| Field | Frontend Usage |
|-------|----------------|
| `data` | Infrastructure/lookup - not directly displayed |

---

### `datasets_subsidyj51`

**Row count:** 27,762

#### Always Populated (16 fields)

| Field | Frontend Usage |
|-------|----------------|
| `address` | Not used by frontend |
| `bbl` | Not used by frontend |
| `block` | Not used by frontend |
| `borough` | Not used by frontend |
| `buildingclassatpresent` | Not used by frontend |
| `buildingclasscategory` | Not used by frontend |
| `commercialunits` | Not used by frontend |
| `grosssquarefeet` | Not used by frontend |
| `landsquarefeet` | Not used by frontend |
| `lot` | Not used by frontend |
| `neighborhood` | Not used by frontend |
| `residentialunits` | Not used by frontend |
| `taxclassatpresent` | Not used by frontend |
| `totalunits` | Not used by frontend |
| `yearbuilt` | Not used by frontend |
| `zipcode` | Not used by frontend |

---

### `datasets_taxlien`

**Row count:** 6,562

#### Partially Populated (5 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `communityboard` | 6,469 | 93 | 98.6% | Not used by frontend |
| `councildistrict` | 6,489 | 73 | 98.9% | Not used by frontend |
| `housenumber` | 5,880 | 682 | 89.6% | Not used by frontend |
| `streetname` | 6,555 | 7 | 99.9% | Not used by frontend |
| `zipcode` | 6,047 | 515 | 92.2% | Not used by frontend |

#### Always Populated (10 fields)

| Field | Frontend Usage |
|-------|----------------|
| `bbl` | Not used by frontend |
| `block` | Not used by frontend |
| `borough` | Not used by frontend |
| `buildingclass` | Not used by frontend |
| `cycle` | Not used by frontend |
| `lot` | Not used by frontend |
| `month` | Not used by frontend |
| `taxclasscode` | Not used by frontend |
| `waterdebtonly` | Not used by frontend |
| `year` | Not used by frontend |

---

### `datasets_taxlot`

**Row count:** 1,138,745

#### Partially Populated (3 fields)

| Field | Non-Null | Null | Populated % | Frontend Usage |
|-------|----------|------|-------------|----------------|
| `bbbl` | 289,043 | 849,702 | 25.4% | Infrastructure/lookup - not directly displayed |
| `condonum` | 297,625 | 841,120 | 26.1% | Infrastructure/lookup - not directly displayed |
| `coopnum` | 7,736 | 1,131,009 | 0.7% | Infrastructure/lookup - not directly displayed |

#### Always Populated (6 fields)

| Field | Frontend Usage |
|-------|----------------|
| `bbl` | Infrastructure/lookup - not directly displayed |
| `condoflag` | Infrastructure/lookup - not directly displayed |
| `interior` | Infrastructure/lookup - not directly displayed |
| `numaddr` | Infrastructure/lookup - not directly displayed |
| `numbf` | Infrastructure/lookup - not directly displayed |
| `vacant` | Infrastructure/lookup - not directly displayed |

---

### `datasets_zipcode`

**Row count:** 226

#### Always Populated (1 fields)

| Field | Frontend Usage |
|-------|----------------|
| `data` | Infrastructure/lookup - not directly displayed |

---
