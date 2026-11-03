// Premiere side (ExtendScript): read the selected clip of the timeline and put the improved file back.
// Values go back to the panel as a hand-built JSON string (older ExtendScript engines have no JSON object).

function _q(s) { return '"' + String(s).replace(/\\/g, '\\\\').replace(/"/g, '\\"') + '"'; }

function mv_getSelectedClip() {
    var seq = app.project.activeSequence;
    if (!seq) return '{"error":"No hay ninguna secuencia abierta."}';
    var sel = seq.getSelection();
    var item = null;
    for (var i = 0; i < sel.length; i++) {
        if (sel[i].mediaType === 'Video' && sel[i].projectItem) { item = sel[i]; break; }
    }
    if (!item) return '{"error":"Selecciona un clip de video en la linea de tiempo."}';
    var path = item.projectItem.getMediaPath();
    if (!path) return '{"error":"El clip seleccionado no tiene un archivo de video (es un grafico, color o secuencia anidada)."}';
    // which video track holds it
    var track = -1;
    for (var t = 0; t < seq.videoTracks.numTracks && track < 0; t++) {
        var clips = seq.videoTracks[t].clips;
        for (var c = 0; c < clips.numItems; c++) {
            if (clips[c].nodeId === item.nodeId) { track = t; break; }
        }
    }
    var seqFps = 1 / seq.getSettings().videoFrameRate.seconds;
    var speed = 1;
    try { speed = item.getSpeed(); } catch (e) {}
    return '{"path":' + _q(path) +
        ',"name":' + _q(item.name) +
        ',"in":' + item.inPoint.seconds +
        ',"out":' + item.outPoint.seconds +
        ',"start":' + item.start.seconds +
        ',"track":' + track +
        ',"tracks":' + seq.videoTracks.numTracks +
        ',"seqFps":' + seqFps +
        ',"speed":' + speed +
        ',"project":' + _q(app.project.path) + '}';
}

function _findBin(name) {
    var root = app.project.rootItem;
    for (var i = 0; i < root.children.numItems; i++) {
        var it = root.children[i];
        if (it.type === ProjectItemType.BIN && it.name === name) return it;
    }
    return root.createBin(name);
}

function _findItem(bin, fileName) {
    for (var i = bin.children.numItems - 1; i >= 0; i--) {
        var it = bin.children[i];
        var p = it.getMediaPath ? it.getMediaPath() : '';
        if (p && p.replace(/\\/g, '/').split('/').pop() === fileName) return it;
    }
    return null;
}

// Imports the improved clip into the "Mejorados" bin and lays it on the track ABOVE the original, at the
// same time position (the original stays underneath, untouched). If there is no track above, it replaces
// the original on its own track.
function mv_importAndPlace(filePath, startSeconds, trackIndex) {
    var bin = _findBin('Mejorados (IA)');
    var ok = app.project.importFiles([filePath], true, bin, false);
    if (!ok) return '{"error":"Premiere no pudo importar el archivo."}';
    var fileName = filePath.replace(/\\/g, '/').split('/').pop();
    var pi = _findItem(bin, fileName);
    if (!pi) return '{"error":"Importado, pero no lo encuentro en el bin Mejorados (IA)."}';
    var seq = app.project.activeSequence;
    var target = (trackIndex + 1 < seq.videoTracks.numTracks) ? trackIndex + 1 : trackIndex;
    seq.videoTracks[target].overwriteClip(pi, startSeconds);
    return '{"ok":true,"track":' + (target + 1) + ',"replaced":' + (target === trackIndex) + '}';
}
