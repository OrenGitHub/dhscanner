<?php

use Dompdf\Dompdf;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

class SomeClassTheAppLoaded
{
    public $data = null;
    public function __construct($data) { $this->data = $data; }

    # POP heaven ...  a destructor with system exec ...
    public function __destruct() { system($this->data); }
}

Route::get('/token', function() { return csrf_token(); });

Route::get('/status', function() {
    if (file_exists('/frontend/public/pwned')) {
        return "You've been pwned !\n";
    } else {
        return "Everything seems fine\n";
    }
});

Route::post('/upload/profile/photo', function (Request $request) {
    $file = $request->file('profile');
    $content = file_get_contents($file);
    file_put_contents("/uploads/v1/user/profile.png", $content);
    return "saved profile picture to /uploads/v1/user/profile.png";
});

Route::post('/test', function(Request $request) {
    return "999 666 MMM";
});

Route::post('/ghsa_97m3', function (Request $request) {

    $file = $request->file('source');
    $content = file_get_contents($file);

    $dompdf = new Dompdf();
    $dompdf->loadHtml($content);
    $dompdf->setPaper('A4', 'landscape');
    $options = $dompdf->getOptions();
    $options->setAllowedProtocols([]);
    $dompdf->render();
    $dompdf->stream();

    return "DDD 444 111";
});

