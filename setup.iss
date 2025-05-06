[Setup]
AppId={{7eece18b-e098-4cdf-aa29-8a64c73d005a}} ; ← mantenha este AppId fixo!
AppName=Gerenciador PDF
AppVersion=1.0.4
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
; Inclui os arquivos do build gerado pelo cx_Freeze
Source: "build\exe.win-amd64-3.13\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

; Copia toda a estrutura do Ghostscript (incluindo bin/)
Source: "gs\*"; DestDir: "{app}\gs"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Atalho no menu iniciar
Name: "{autoprograms}\Gerenciador PDF"; Filename: "{app}\Gerenciador PDF.exe"; IconFilename: "{app}\resources\icons\icone_gerenciador.ico"

; Atalho na área de trabalho (opcional)
Name: "{userdesktop}\Gerenciador PDF"; Filename: "{app}\Gerenciador PDF.exe"; IconFilename: "{app}\resources\icons\icone_gerenciador.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Área de Trabalho"; GroupDescription: "Opções adicionais:"

[Registry]
; Adiciona o bin do Ghostscript ao PATH do usuário (sem exigir admin)
Root: HKCU; Subkey: "Environment";
ValueType: expandsz;
ValueName: "Path";
ValueData: "{olddata};{app}\gs\gs10.05.0\bin";
Flags: preservestringtype

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  NeedsRestart: Boolean;
begin
  if CurStep = ssPostInstall then
  begin
    // Atualiza as variáveis de ambiente em tempo de execução
    NeedsRestart := True;
    SendMessageTimeout(HWND_BROADCAST, WM_SETTINGCHANGE, 0,
      LongInt(PChar('Environment')), SMTO_ABORTIFHUNG, 5000, NeedsRestart);
  end;
end;

[Run]
; Executa o programa após instalação (caso usuário aceite)
Filename: "{app}\Gerenciador PDF.exe"; Description: "Executar Gerenciador PDF"; Flags: nowait postinstall skipifsilent
