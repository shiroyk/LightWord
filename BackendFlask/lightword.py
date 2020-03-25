import os
import sys
import click
import logging, logging.config
from sqlalchemy.engine import reflection
from flask_migrate import stamp
from app import create_app, db
from app.models import Vocabulary, VocabType, VocabData
from config.config import Config

app = create_app(Config)
gunicorn_logger = logging.getLogger('gunicorn.error')
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

@app.cli.command()
@click.option('--recreate', default=False, help='Warning!!! Recreate database')
def initdb(recreate):
    if recreate == "yes":
        db.drop_all()
    tables = reflection.Inspector.from_engine(db.engine)
    if not tables.get_table_names():
        db.create_all()
        stamp()
        click.echo('%s: Initialized database.' % __name__)
    else:
        raise click.ClickException('Database already exist.')

@app.cli.command()
@click.option('--path', default=False, help='Import Vocabulary from csv file')
def vocabulary(path):
    click.echo("%s: processing..." % __name__)

    result = []
    with open(path,'rb') as f:
        for line in f:
            v = line.decode().split(',', 2)
            result.append({"word": v[0], "frequency": v[1], "localdict": v[2]})
    try:
        db.session.bulk_insert_mappings(Vocabulary, result)
        click.echo("%s: Import Vocabulary complete" % __name__)
    except:
        click.ClickException('Import Vocabulary failed')

@app.cli.command()
@click.option('--path', default=False, help='Import Vocabdata from txt file') 
def vocabdata(path):
    click.echo("%s: processing..." % __name__)

    filename = path.split('/')[-1].split('.')[0]

    with open(path,'rb') as f:
            count = 1
            while True:
                data = f.read(65536)
                if not data: break
                count += data.count(b'\n')
    vtype = VocabType.vtype_insert({'vocabtype': filename, 'amount': count})

    vocabulary = {}
    for x in Vocabulary.query.all():
        vocabulary.update({x.word: [x.id, x.frequency]})

    result = []
    with open(path,'rb') as f:
        for line in f:
            word = line.decode().rstrip()
            try:
                v = vocabulary[word]
                result.append({"word_id": v[0], "vtype_id": vtype, "frequency": v[1]})
            except KeyError:
                click.echo("%s: Word %s no found vocabulary data" % (__name__, word) )
    try:
        db.session.bulk_insert_mappings(VocabData, result)
        click.echo("%s: Import Vocabdata complete" % __name__)
    except:
        click.ClickException("Import Vocabdata failed")

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

@app.cli.command()
@click.option('--coverage/--no-coverage', default=False,
              help='Run tests under code coverage.')
def test(coverage):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()