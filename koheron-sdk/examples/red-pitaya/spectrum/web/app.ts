class App {

    public laserDriver: LaserDriver;
    public laserControl: LaserControl;
    public spectrum: Spectrum;
    public modulationDriver: ModulationDriver;
    public modulationControl: ModulationControl;
    public average: Average;
    public plot: Plot;
    private navigation: Navigation;

    wfmSize = 8192;
    samplingRate = 125e6;

    constructor(window: Window, document: Document,
                ip: string, plot_placeholder: JQuery) {
        let client = new Client(ip, 5);

        window.addEventListener('load', () => {
            client.init( () => {
                this.laserDriver = new LaserDriver(client);
                this.laserControl = new LaserControl(document, this.laserDriver);
                this.spectrum = new Spectrum(client);
                this.average = new Average(document, this.spectrum);
                this.modulationDriver = new ModulationDriver(client);
                this.modulationControl = new ModulationControl(document, this.modulationDriver, this.wfmSize, this.samplingRate);
                this.plot = new Plot(document, plot_placeholder, this.spectrum);
                this.navigation = new Navigation(document);
            });
        }, false);

        window.onbeforeunload = () => { client.exit(); };

    }
}

let app = new App(window, document, location.hostname, $('#plot-placeholder'));