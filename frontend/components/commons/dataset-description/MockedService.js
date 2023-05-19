const FAKE_DESCRIPTION = `<h1 class="code-line" data-line-start=0 data-line-end=1 ><a id="Lorem_Ipsum_0"></a>Lorem Ipsum</h1>
<p class="has-line-data" data-line-start="1" data-line-end="2">Es simplemente el texto de relleno de las imprentas y archivos de texto. Lorem Ipsum ha sido el texto de relleno estándar de las industrias desde el año 1500, cuando un impresor (N. del T. persona que se dedica a la imprenta) desconocido usó una galería de textos y los mezcló de tal manera que logró hacer un libro de textos especimen. No sólo sobrevivió 500 años, sino que tambien ingresó como texto de relleno en documentos electrónicos, quedando esencialmente igual al original. Fue popularizado en los 60s con la creación de las hojas “Letraset”, las cuales contenian pasajes de Lorem Ipsum, y más recientemente con software de autoedición, como por ejemplo Aldus PageMaker, el cual incluye versiones de Lorem Ipsum.</p>
<h2 class="code-line" data-line-start=3 data-line-end=4 ><a id="Code_3"></a>Code</h2>
<pre><code class="has-line-data" data-line-start="5" data-line-end="7" class="language-js">Test
</code></pre>`;

export const getDatasetDescription = (datasetId, datasetTask) => {
    return FAKE_DESCRIPTION
}

export const saveDescription = (datasetId, datasetTask, newDescription) => {
    return Promise.resolve();
}