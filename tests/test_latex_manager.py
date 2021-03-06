import os
import pytest
import pathlib

import numpy as np

import bibmanager.utils as u
import bibmanager.bib_manager   as bm
import bibmanager.latex_manager as lm


def test_no_comments():
    assert lm.no_comments("") == ""
    assert lm.no_comments("Hello world.") == "Hello world."
    assert lm.no_comments("inline comment % comment") == "inline comment"
    assert lm.no_comments("% comment line.") == ""
    assert lm.no_comments("percentage \\%") == "percentage \\%"
    # If first line is comment, '\n' stays:
    assert lm.no_comments("% comment line.\nThen this") == "\nThen this"
    # If not, entire line is removed (including '\n'):
    assert lm.no_comments("Line\n%comment\nanother line") \
                       == "Line\nanother line"


def test_citations1():
    cites = lm.citations("\\citep{Author}.")
    assert next(cites) == "Author"
    cites = lm.citations("\\citep{\n Author }.")
    assert next(cites) == "Author"
    cites = lm.citations("\\citep[pre]{Author}.")
    assert next(cites) == "Author"
    cites = lm.citations("\\citep[pre][post]{Author}.")
    assert next(cites) == "Author"
    cites = lm.citations("\\citep\n[][]{Author}.")
    assert next(cites) == "Author"
    cites = lm.citations("\\citep [pre] [post] {Author}.")
    assert next(cites) == "Author"
    cites = lm.citations("\\citep[{\\pre},][post]{Author}.")
    assert next(cites) == "Author"
    # Outer commas are ignored:
    cites = lm.citations("\\citep{,Author,}.")
    assert next(cites) == "Author"

def test_citations2():
    # Multiple citations:
    cites = lm.citations("\\citep[{\\pre},][post]{Author1, Author2}.")
    assert next(cites) == "Author1"
    assert next(cites) == "Author2"
    cites = lm.citations(
                "\\citep[pre][post]{Author1} and \\citep[pre][post]{Author2}.")
    assert next(cites) == "Author1"
    assert next(cites) == "Author2"
    cites = lm.citations("\\citep[pre\n ][post] {Author1, Author2}")
    assert next(cites) == "Author1"
    assert next(cites) == "Author2"

def test_citations3():
    # Recursive citations:
    cites = lm.citations(
        "\\citep[see also \\citealp{Author1}][\\citealp{Author3}]{Author2}")
    assert next(cites) == "Author1"
    assert next(cites) == "Author2"
    assert next(cites) == "Author3"

def test_citations4():
    # Match all of these:
    assert next(lm.citations("\\cite{AuthorA}"))          == "AuthorA"
    assert next(lm.citations("\\nocite{AuthorB}"))        == "AuthorB"
    assert next(lm.citations("\\defcitealias{AuthorC}"))  == "AuthorC"
    assert next(lm.citations("\\citet{AuthorD}"))         == "AuthorD"
    assert next(lm.citations("\\citet*{AuthorE}"))        == "AuthorE"
    assert next(lm.citations("\\Citet{AuthorF}"))         == "AuthorF"
    assert next(lm.citations("\\Citet*{AuthorG}"))        == "AuthorG"
    assert next(lm.citations("\\citep{AuthorH}"))         == "AuthorH"
    assert next(lm.citations("\\citep*{AuthorI}"))        == "AuthorI"
    assert next(lm.citations("\\Citep{AuthorJ}"))         == "AuthorJ"
    assert next(lm.citations("\\Citep*{AuthorK}"))        == "AuthorK"
    assert next(lm.citations("\\citealt{AuthorL}"))       == "AuthorL"
    assert next(lm.citations("\\citealt*{AuthorM}"))      == "AuthorM"
    assert next(lm.citations("\\Citealt{AuthorN}"))       == "AuthorN"
    assert next(lm.citations("\\Citealt*{AuthorO}"))      == "AuthorO"
    assert next(lm.citations("\\citealp{AuthorP}"))       == "AuthorP"
    assert next(lm.citations("\\citealp*{AuthorQ}"))      == "AuthorQ"
    assert next(lm.citations("\\Citealp{AuthorR}"))       == "AuthorR"
    assert next(lm.citations("\\Citealp*{AuthorS}"))      == "AuthorS"
    assert next(lm.citations("\\citeauthor{AuthorT}"))    == "AuthorT"
    assert next(lm.citations("\\citeauthor*{AuthorU}"))   == "AuthorU"
    assert next(lm.citations("\\Citeauthor{AuthorV}"))    == "AuthorV"
    assert next(lm.citations("\\Citeauthor*{AuthorW}"))   == "AuthorW"
    assert next(lm.citations("\\citeyear{AuthorX}"))      == "AuthorX"
    assert next(lm.citations("\\citeyear*{AuthorY}"))     == "AuthorY"
    assert next(lm.citations("\\citeyearpar{AuthorZ}"))   == "AuthorZ"
    assert next(lm.citations("\\citeyearpar*{AuthorAA}")) == "AuthorAA"

def test_citations5():
    # The sample tex file:
    texfile = os.path.expanduser('~') + "/.bibmanager/examples/sample.tex"
    with open(texfile) as f:
        tex = f.read()
    tex = lm.no_comments(tex)
    cites = [citation for citation in lm.citations(tex)]
    assert cites == [
        'AASteamHendrickson2018aastex62',
        'vanderWaltEtal2011numpy',
        'JonesEtal2001scipy',
        'Hunter2007ieeeMatplotlib',
        'PerezGranger2007cseIPython',
        'MeurerEtal2017pjcsSYMPY',
        'Astropycollab2013aaAstropy',
        'AASteamHendrickson2018aastex62']


def test_build_bib_inplace(mock_init):
    bm.merge(u.HOME+"examples/sample.bib")
    os.chdir(u.HOME+"examples")
    missing = lm.build_bib("sample.tex")
    files = os.listdir(".")
    assert "texsample.bib" in files
    # Now check content:
    np.testing.assert_array_equal(missing, np.zeros(0,dtype="U"))
    bibs = bm.loadfile("texsample.bib")
    assert len(bibs) == 7
    keys = [bib.key for bib in bibs]
    assert "AASteamHendrickson2018aastex62" in keys
    assert "vanderWaltEtal2011numpy"    in keys
    assert "JonesEtal2001scipy"         in keys
    assert "Hunter2007ieeeMatplotlib"   in keys
    assert "PerezGranger2007cseIPython" in keys
    assert "MeurerEtal2017pjcsSYMPY"    in keys
    assert "Astropycollab2013aaAstropy" in keys


def test_build_bib_remote(mock_init):
    bm.merge(u.HOME+"examples/sample.bib")
    lm.build_bib(u.HOME+"examples/sample.tex")
    files = os.listdir(u.HOME+"examples/")
    assert "texsample.bib" in files


def test_build_bib_user_bibfile(mock_init):
    bm.merge(u.HOME+"examples/sample.bib")
    lm.build_bib(u.HOME+"examples/sample.tex", bibfile=u.HOME+"my_file.bib")
    files = os.listdir(u.HOME)
    assert "my_file.bib" in files


def test_build_bib_missing(capsys, mock_init):
    # Assert screen output:
    bm.merge(u.HOME+"examples/sample.bib")
    captured = capsys.readouterr()
    texfile = u.HOME+"examples/mock_file.tex"
    with open(texfile, "w") as f:
        f.write("\\cite{Astropycollab2013aaAstropy} \\cite{MissingEtal2019}.\n")
    missing = lm.build_bib(texfile, u.HOME+"my_file.bib")
    captured = capsys.readouterr()
    assert captured.out == "References not found:\nMissingEtal2019\n"
    # Check content:
    np.testing.assert_array_equal(missing, np.array(["MissingEtal2019"]))
    bibs = bm.loadfile(u.HOME+"my_file.bib")
    assert len(bibs) == 1
    assert "Astropycollab2013aaAstropy" in bibs[0].key


def test_build_raise(mock_init):
    bm.merge(u.HOME+"examples/sample.bib")
    with open(u.HOME+"examples/mock_file.tex", "w") as f:
        f.write("\\cite{Astropycollab2013aaAstropy}")
    with pytest.raises(Exception,
             match="No 'bibiliography' call found in tex file."):
        lm.build_bib(u.HOME+"examples/mock_file.tex")


def test_clear_latex(mock_init):
    # Mock some 'latex output' files:
    pathlib.Path(u.HOME+"examples/sample.pdf").touch()
    pathlib.Path(u.HOME+"examples/sample.ps").touch()
    pathlib.Path(u.HOME+"examples/sample.bbl").touch()
    pathlib.Path(u.HOME+"examples/sample.dvi").touch()
    pathlib.Path(u.HOME+"examples/sample.out").touch()
    pathlib.Path(u.HOME+"examples/sample.blg").touch()
    pathlib.Path(u.HOME+"examples/sample.log").touch()
    pathlib.Path(u.HOME+"examples/sample.aux").touch()
    pathlib.Path(u.HOME+"examples/sample.lof").touch()
    pathlib.Path(u.HOME+"examples/sample.lot").touch()
    pathlib.Path(u.HOME+"examples/sample.toc").touch()
    pathlib.Path(u.HOME+"examples/sampleNotes.bib").touch()
    # Here they are:
    files = os.listdir(u.HOME+"examples")
    assert len(files) == 17
    lm.clear_latex(u.HOME+"examples/sample.tex")
    # Now they are gone:
    files = os.listdir(u.HOME+"examples")
    assert set(files) \
        == set(['aastex62.cls', 'apj_hyperref.bst', 'sample.bib', 'sample.tex',
                'top-apj.tex'])

@pytest.mark.skip(reason="Need to either mock latex, bibtex, dvi2df calls or learn how to enable them in travis CI")
def test_compile_latex():
    # Either mock heavily the latex, bibtex, dvi-pdf calls or learn how
    # to integrate them to CI.
    pass

@pytest.mark.skip(reason="Need to either mock pdflatex and bibtex calls or learn how to enable them in travis CI")
def test_compile_pdflatex():
    # Same as test_compile_latex.
    pass
