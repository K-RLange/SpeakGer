[![Paper](https://badgen.net/badge/paper/CPSS@Konvens23/red?icon=firefox)](https://lwus.statistik.tu-dortmund.de/) [![Data set](https://badgen.net/badge/dataset/BERD@NFDI/green?icon=firefox)](mailto:kalange@statistik.tu-dortmund.de)
# SpeakGer
This GitHub-repository provides an overview of the functions used to create the "SpeakGer" data set. It consists of a total of 15,452,593 speeches of German politicians from the German Bundestag as well as all 16 German federal state parliaments from 1949 to 2023. We aim to update this data set on a regular basis so that the plenary sessions stay up to date.

## Citation
When using this data set in your work, please cite
```
@inproceedings{SpeakGer,
  authors={Lange, Kai-Robin and Jentsch, Carsten},
  title={SpeakGer: A meta-data enriched speech corpus of German state and federal parliaments},
  booktitle={Proceedings of the 3rd Workshop on Computational Linguistics for Political Text Analysis},
  year={2023},
  moth={sep}
}

```
## Download and data structure
As the download-platform BERD@NFDI is currently in its beta-phase, there is currently no public access to the corpus yet. You can however write me a mail and you be granted free access to the beta-version of the platform and be able to download the corpus.

The meta data is separated into two different types: time-specific meta-data that contains pnly information for a legislative period but can change over time (e.g. the party or constituency of an mp) and meta-data that is considered fixed, such as the birth date or the name of a speaker. The former information are stored aong with the speeches as it is considered temporal information of that point in time, but are additionally stored in the file all_mps_mapping.csv if there is the need to double-check something. The rest of the meta-data are stored in the file all_mps_meta.csv. The meta-data from this file can be matched with a speech by comparing the speaker ID-variable "MPID".
The speeches of each parliament are saved in a csv format. Along with the speeches, they contain the following meta-data:
- Period: int. The period in which the speech took place
- Session: int. The session in which the speech took place
- Chair: boolean. The information if the speaker was the chair of the plenary session
- Interjection: voolean. The information if the speech is a comment or an interjection from the crowd
- Party: list (e.g. \["cdu"\] or \["cdu", "fdp"\] when having more than one speaker during an interjection). List of the party of the speaker or the parties whom the comment/interjection references 
- Consituency: string. The consituency of the speaker in the current legislative period
- MPID: int. The ID of the speaker, which can be used to get more meta-data from the file all_mps_meta.csv

The file all_mps_meta.csv contains the following meta information:
- MPID: int. The ID of the speaker, which can be used to match the mp with his/her speeches.
- WikipediaLink: The Link to the mps Wikipedia page
- WikiDataLink: The Link to the mps WikiData page
- Name: string. The full name of the mp.
- Last Name: string. The last name of the mp, found on WikiData. If no last name is given on WikiData, the full name was heuristically cut at the last space to get the information neccessary for splitting the speeches.
- Born: string, format: YYYY-MM-DD. Birth date of the mp. If an exact birth date is found on WikiData, this exact date is used. Otherwise, a day in the year of birth given on Wikipedia is used.
- SexOrGender: string. Information on the sex or gender of the mp. Disclaimer: This infomation was taken from WikiData, which does not seem to differentiate between sex or gender.
- Occupation: list. Occupation(s) of the mp.
- Religion: string. Religious believes of the mp.
- AbgeordnetenwatchID: int. ID of the mp on the website [Abgeordnetenewatch](https://www.abgeordnetenwatch.de/).

## Usage for qualitative research
Currently, there is no option to process the corpus in a qualitative way such as e.g. [Open Parliament TV](https://openparliament.tv/). We are however open to enabling users to process the speeches in a similar way in the future if we find an appropiate way of doing so.

## Intended usage and Legal Notice
We intend this corpus to be used for research purposes only and condemn using it for political framing.
We take no responsibility for the correctness of the meta data provided here as they only display publicly available information that can be found on WikiData and Wikipedia. We also take no responsibility if a speech or meta data was assigned to the wrong mp. If you notice such a mistake in the data set, please open an Issue so that we can identify and fix the problem.
