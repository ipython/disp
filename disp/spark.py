#!/usr/bin/env python
# -*- coding: utf-8 -*-


def fully_qualified_name(m):
    return (m.__module__ + "." if hasattr(m, "__module__") else "") + m.__class__.__name__


def repr_spark_context_html(sc):
    '''
    Carry over from the Spark 2.2.0 _repr_html_ for spark contexts

    Works on objects whose fully qualified name is 'pyspark.context.SparkContext'
    '''
    return """
    <div>
        <p><b>SparkContext</b></p>

        <p><a href="{sc.uiWebUrl}">Spark UI</a></p>

        <dl>
          <dt>Version</dt>
            <dd><code>v{sc.version}</code></dd>
          <dt>Master</dt>
            <dd><code>{sc.master}</code></dd>
          <dt>AppName</dt>
            <dd><code>{sc.appName}</code></dd>
        </dl>
    </div>
    """.format(
        sc=sc
    )


def repr_spark_session_html(session):
    '''
    Carry over from the Spark 2.2.0 _repr_html_ for spark sessions

    Works on objects whose fully qualified name is 'pyspark.sql.session.SparkSession'
    '''
    return """
        <div>
            <p><b>SparkSession - {catalogImplementation}</b></p>
            {sc_HTML}
        </div>
    """.format(
        catalogImplementation=session.conf.get("spark.sql.catalogImplementation"),
        sc_HTML=repr_sc(session.sparkContext)
    )
