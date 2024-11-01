// Fungsi ini akan dieksekusi ketika halaman HTML telah dimuat sepenuhnya
document.addEventListener('DOMContentLoaded', function () {
    // Mengambil elemen-elemen yang diperlukan dari halaman HTML
    const recipesLink = document.getElementById('recipes-link'); // Link untuk menu Resep Masakan
    const bookmarksLink = document.getElementById('bookmarks-link'); // Link untuk menu Bookmark
    const recipes = document.getElementById('recipes'); // Daftar resep masakan
    const bookmarks = document.getElementById('bookmarks'); // Daftar bookmark
    const bookmarkList = document.getElementById('bookmark-list'); // Daftar resep yang telah di-bookmark
    const recipeButtons = document.querySelectorAll('.bookmark-btn'); // Tombol bookmark pada setiap resep

    // Event listener untuk menu Resep Masakan
    recipesLink.addEventListener('click', () => {
        recipes.style.display = 'flex'; // Tampilkan daftar resep
        bookmarks.style.display = 'none'; // Sembunyikan daftar bookmark
    });

    // Event listener untuk menu Bookmark
    bookmarksLink.addEventListener('click', () => {
        recipes.style.display = 'none'; // Sembunyikan daftar resep
        bookmarks.style.display = 'block'; // Tampilkan daftar bookmark
    });

    // Fungsi untuk menambahkan resep ke daftar bookmark
    function bookmark(recipeName) {
        const li = document.createElement('li'); // Membuat elemen <li> baru
        li.textContent = recipeName; // Menambahkan nama resep ke teks di dalam elemen <li>
        const unbookmarkButton = document.createElement('button'); // Membuat elemen <button> untuk tombol unbookmark
        unbookmarkButton.textContent = 'Unbookmark'; // Menambahkan teks 'Unbookmark' ke dalam tombol unbookmark
        unbookmarkButton.classList.add('unbookmark-btn'); // Menambahkan kelas 'unbookmark-btn' ke dalam elemen <button>
        // Event listener untuk menghapus resep dari daftar bookmark saat tombol unbookmark diklik
        unbookmarkButton.addEventListener('click', () => {
            li.remove(); // Menghapus elemen <li> (reseps) dari daftar bookmark
        });
        li.appendChild(unbookmarkButton); // Menambahkan tombol unbookmark ke dalam elemen <li>
        bookmarkList.appendChild(li); // Menambahkan elemen <li> ke dalam daftar bookmark
    }

    // Event listener untuk setiap tombol bookmark pada resep
    recipeButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault(); // Mencegah aksi default dari tombol bookmark (misalnya, mengirimkan formulir)
            const recipeName = e.target.previousElementSibling.textContent; // Mengambil nama resep dari elemen sebelumnya (h2)
            bookmark(recipeName); // Memanggil fungsi bookmark untuk menambahkan resep ke daftar bookmark
        });
    });
});
