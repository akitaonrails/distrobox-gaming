using System;
using System.IO;
using LibHac;
using LibHac.Common;
using LibHac.Common.Keys;
using LibHac.Fs;
using LibHac.Fs.Fsa;
using LibHac.FsSystem;
using LibHac.Tools.Fs;
using LibHac.Tools.FsSystem;
using LibHac.Tools.FsSystem.NcaUtils;
using Path = System.IO.Path;

// One-time recovery tool for the UltraTears dump (docs/ultratears.md).
//
// UltraTears refuses encrypted packages (.xci/.nsp/.nca) and reads no keys, so
// it needs the ExeFS + RomFS of Tears of the Kingdom with update 1.4.3 already
// applied, as plain files. Merging the base RomFS with the update's BKTR
// (indirect / AES-CTR-EX) patch is something only the full .NET LibHac does —
// hactool (even git master) reports "Invalid BKTR layout" on 1.4.3, and the
// Rust ports do not implement BKTR. LibHac 0.19.0 comes from NuGet
// (nuget.org/packages/LibHac), independent of the DMCA'd GitHub mirrors.
//
//   dotnet run -c Release -- <base.xci> <update.nsp> <prod.keys> <title.keys> <outDir>
//
// title.keys holds the ENCRYPTED titlekey (rights_id = enc_titlekey); LibHac
// decrypts it with the titlekek internally.

class Program
{
    static int Main(string[] args)
    {
        if (args.Length < 5)
        {
            Console.Error.WriteLine("usage: UtExtract <base.xci> <update.nsp> <prod.keys> <title.keys> <outDir>");
            return 2;
        }
        string baseXci = args[0], updNsp = args[1], prodKeys = args[2], titleKeys = args[3], outDir = args[4];

        KeySet keySet = KeySet.CreateDefaultKeySet();
        ExternalKeyReader.ReadKeyFile(keySet, prodKeys, titleKeys, (string)null, (IProgressReport)null);

        // --- base program NCA from the XCI secure partition ---
        var xciStorage = new LocalStorage(baseXci, FileAccess.Read);
        var xci = new Xci(keySet, xciStorage);
        IFileSystem securePart = xci.OpenPartition(XciPartitionType.Secure);
        Nca baseProg = FindProgramNca(keySet, securePart);
        Console.WriteLine($"base program NCA: TitleId={baseProg.Header.TitleId:x16}");

        // --- patch program NCA from the update NSP ---
        var nspStorage = new LocalStorage(updNsp, FileAccess.Read);
        var pfs = new PartitionFileSystem();
        pfs.Initialize(nspStorage).ThrowIfFailure();
        Nca patchProg = FindProgramNca(keySet, pfs);
        Console.WriteLine($"patch program NCA: TitleId={patchProg.Header.TitleId:x16}");

        // --- romfs = base data section patched by update (BKTR) ---
        IFileSystem romfs = baseProg.OpenFileSystemWithPatch(patchProg, NcaSectionType.Data, IntegrityCheckLevel.ErrorOnInvalid);

        // --- exefs = patch code section (full, not BKTR); fall back to base ---
        IFileSystem exefs;
        try { exefs = patchProg.OpenFileSystem(NcaSectionType.Code, IntegrityCheckLevel.ErrorOnInvalid); }
        catch { exefs = baseProg.OpenFileSystem(NcaSectionType.Code, IntegrityCheckLevel.ErrorOnInvalid); }

        Extract(exefs, Path.Combine(outDir, "exefs"));
        Extract(romfs, Path.Combine(outDir, "romfs"));
        Console.WriteLine("DONE");
        return 0;
    }

    static Nca FindProgramNca(KeySet keySet, IFileSystem fs)
    {
        foreach (DirectoryEntryEx entry in fs.EnumerateEntries("/", "*.nca"))
        {
            using var file = new UniqueRef<IFile>();
            fs.OpenFile(ref file.Ref, entry.FullPath.ToU8Span(), OpenMode.Read).ThrowIfFailure();
            var nca = new Nca(keySet, file.Release().AsStorage());
            if (nca.Header.ContentType == NcaContentType.Program)
                return nca;
        }
        throw new InvalidDataException("no Program NCA found");
    }

    static void Extract(IFileSystem fs, string outDir)
    {
        Directory.CreateDirectory(outDir);
        int n = 0;
        foreach (DirectoryEntryEx entry in fs.EnumerateEntries("/", "*", SearchOptions.RecurseSubdirectories))
        {
            if (entry.Type != DirectoryEntryType.File) continue;
            string rel = entry.FullPath.TrimStart('/').Replace('/', Path.DirectorySeparatorChar);
            string dest = Path.Combine(outDir, rel);
            Directory.CreateDirectory(Path.GetDirectoryName(dest)!);

            using var file = new UniqueRef<IFile>();
            fs.OpenFile(ref file.Ref, entry.FullPath.ToU8Span(), OpenMode.Read).ThrowIfFailure();
            file.Get.GetSize(out long size).ThrowIfFailure();

            using var dst = File.Create(dest);
            byte[] buf = new byte[1 << 20];
            long off = 0;
            while (off < size)
            {
                int toRead = (int)Math.Min(buf.Length, size - off);
                file.Get.Read(out long br, off, buf.AsSpan(0, toRead), ReadOption.None).ThrowIfFailure();
                if (br <= 0) break;
                dst.Write(buf, 0, (int)br);
                off += br;
            }
            n++;
        }
        Console.WriteLine($"extracted {n} files -> {outDir}");
    }
}
