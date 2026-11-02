"""Real browser regressions. Requires playwright and an installed Chromium browser."""
import argparse
import importlib.util
import json
from pathlib import Path
import tempfile
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('builder', ROOT/'scripts/build.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--browser', help='Chrome/Chromium executable; defaults to Playwright Chromium')
args = parser.parse_args()
data = {'title':'Regression timeline',
        'nodes':[{'id':'input,raw','label':'Input','x':50,'y':100},{'id':'output','label':'Output','x':400,'y':100}],
        'edges':[{'id':'edge,raw','from':'input,raw','to':'output'}],
        'steps':[{'caption':'First','duration':.2,'nodes':['input,raw'],'edges':['edge,raw']},
                 {'caption':'Second','duration':5,'nodes':['output'],'edges':['edge,raw']}]}
with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
    target=Path(tmp)/'regression.html';target.write_text(builder.build(data))
    browser=p.chromium.launch(executable_path=args.browser,headless=True)
    page=browser.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(target.as_uri())
    assert json.loads(page.locator('#stepNodes').input_value())==['input,raw']
    assert json.loads(page.locator('#stepEdges').input_value())==['edge,raw']
    page.locator('#saveStep').click()
    assert page.locator('#status').inner_text()=='步骤已保存'
    assert page.evaluate('diagramStudio.getData().steps[0].nodes')==['input,raw']
    page.locator('#play').click()
    page.wait_for_function('Number(document.getElementById("seek").value) > .5')
    assert page.locator('#stepCaption').input_value()=='Second'
    assert page.locator('.step.active').inner_text().startswith('2.')
    page.locator('#play').click()
    page.locator('#stepCaption').fill('Edited second')
    page.locator('#saveStep').click()
    state=page.evaluate('diagramStudio.getData()')
    assert state['steps'][0]['caption']=='First'
    assert state['steps'][1]['caption']=='Edited second'
    page.locator('#reset').click()
    assert page.locator('#stepCaption').input_value()=='First'
    assert page.locator('.step.active').inner_text().startswith('1.')
    page.locator('#addStep').click()
    assert page.evaluate('diagramStudio.stepAt(Number(document.getElementById("seek").value))')==2
    assert page.locator('.step.active').inner_text().startswith('3.')
    assert not errors,errors
    browser.close()
print('PASS: comma IDs survive unchanged save; playback/pause/reset/add keep editor aligned')
