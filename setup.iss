[Setup]
AppId={{7eece18b-e098-4cdf-aa29-8a64c73d005a}}
AppName=Gerenciador PDF
AppVersion=1.1.4
AppPublisher=Ródiney Wanderson
AppPublisherURL=https://rodineywshare.vercel.app/
AppSupportURL=https://rodineywshare.vercel.app/
DefaultDirName={autopf}\Gerenciador PDF
DefaultGroupName=Gerenciador PDF
OutputDir=dist
OutputBaseFilename=GerenciadorPDF-Setup
Compression=lzma
SolidCompression=yes
SetupIconFile=app\resources\icons\icone_gerenciador.ico
DisableProgramGroupPage=yes
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
UninstallDisplayIcon={app}\Gerenciador PDF.exe
WizardStyle=modern

[Languages]
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"

[Files]
Source: "build\exe.win-amd64-3.13\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "app\resources\icons\icone_gerenciador.ico"; DestDir: "{app}\resources\icons"; Flags: ignoreversion
Source: "gs\*"; DestDir: "{app}\gs"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\Gerenciador PDF"; Filename: "{app}\Gerenciador PDF.exe"; IconFilename: "{app}\resources\icons\icone_gerenciador.ico"
Name: "{userdesktop}\Gerenciador PDF"; Filename: "{app}\Gerenciador PDF.exe"; IconFilename: "{app}\resources\icons\icone_gerenciador.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Área de Trabalho"; GroupDescription: "Opções adicionais:"

[Registry]
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; ValueData: "{olddata};{app}\gs\gs10.05.0\bin"; Flags: preservestringtype

[Run]
Filename: "{app}\Gerenciador PDF.exe"; Description: "Executar Gerenciador PDF"; Flags: nowait postinstall skipifsilent
